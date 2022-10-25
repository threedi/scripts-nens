# installeer openapi_client pip install threedi-api-client
# Let op! Dit werkt alleen als je in {LOKALE_REPO_DIR}\.hg\hgrc je username en password invult onder [paths]:
# [paths]
# default = https://USERNAME:PASSWORD@hg.lizard.net/demomodelslvw

import os
import traceback
from threedi_api_client import ThreediApiClient
from openapi_client.api import ThreedimodelsApi, OrganisationsApi, SimulationsApi
from openapi_client.models.simulation import Simulation

import openapi_client
import datetime
import ast
import time
import subprocess
import re
import shutil
import sqlite3
from osgeo import ogr

SCRIPT_DIR = os.path.dirname(__file__)
local_repo_dir = 'Path_to_local_repo_directory'
api_config = "Path/3di_api_v3/.env" #path to your own api config environment file 
repository_slug = ' --- ' #fill in your own repository slug

organisation_name = 'Nelen & Schuurmans'
simulation_start_date = datetime.date.today()
simulation_start_time = '10:00:00'

deelgebieden_fn = "Path/submodels.txt"

friction_raster_src_dir = 'Path/friction'
infiltration_raster_src_dir = 'Path/infiltration'
dem_raster_src_dir = 'Path/dem'



def commit_and_push(local_repo_dir, commit_message):
    commands = ['hg addremove',
                'hg commit -m "{}"'.format(commit_message),
                'hg push']
    for cmd in commands:
        proc = subprocess.Popen(cmd.split(), cwd=local_repo_dir)
        print(proc.communicate())
        if proc.returncode != 0:
            raise Exception('Commit and push failed')
    revision_nr_str = subprocess.check_output(['hg', 'id', '--num'], cwd=local_repo_dir).decode('utf-8')
    revision_nr = int(re.sub("[^0-9]", "", revision_nr_str))
    return revision_nr


def parse_rain_timeseries(ts, offset=0):
    rain_data = {
        "offset": 0,
        "interpolate": False,
        "values": [[0]],
        "units": "m/s"
    }
    rain_data.update(offset=int(offset))
    timeseries = [list(ast.literal_eval(item)) for item in ts.split('\n')]
    rain_data.update(values=timeseries)
    return rain_data

rain_timeseries = '0,0.00001944444\n3600,0'  # 70 mm /u


def get_revision(models, repository_slug, revision_number: int):
    result = None
    for model_i in models.results:
        if model_i.repository_slug == repository_slug:
            if int(model_i.revision_number) == revision_number:
                result = model_i
    return result


def get_model_when_ready(threedi_models_api, repository_slug, revision_number, max_wait_time):
    seconds = 0
    processed_model = None
    while processed_model is None and seconds < max_wait_time:
        print("\r" + "waiting for inpy ({s} seconds)".format(s=seconds), end="")
        models_list = threedi_models_api.threedimodels_list(limit=100000000)
        processed_model = get_revision(models=models_list, repository_slug=repository_slug,
                                       revision_number=revision_number)
        if processed_model is None:
            time.sleep(5)
            seconds += 5
    print("inpy finished!")
    return processed_model


def simulate(revision_number, inpy_max_wait_time, simulation_name, rain_intensity, rain_duration, simulation_duration):

    # initialisation
    simulation_start_date.strftime("%Y-%m-%d") + 'T' + simulation_start_time
    client = ThreediApiClient(env_file=api_config)
    threedi_models_api = ThreedimodelsApi(client)
    organisations = OrganisationsApi(client)
    organisation_id = organisations.organisations_list(name=organisation_name).results[0].unique_id
    sim_api = SimulationsApi(client)

    selected_model = get_model_when_ready(threedi_models_api=threedi_models_api,
                                          repository_slug=repository_slug,
                                          revision_number=revision_number,
                                          max_wait_time=inpy_max_wait_time)
    # create simulation
    sim = Simulation(
        name=simulation_name,
        threedimodel=selected_model.id,
        organisation=organisation_id,
        start_datetime=simulation_start_date.strftime("%Y-%m-%d") + 'T' + simulation_start_time,
        duration=simulation_duration,
    )
    created_sim = sim_api.simulations_create(sim)

    # add rain events
    sim_api = SimulationsApi(client)
    rain_data = {
        "offset": 0,
        "duration": rain_duration,
        "value": rain_intensity/1000.0/3600.0,
        "units": "m/s"
    }
    sim_api.simulations_events_rain_constant_create(
        created_sim.id, rain_data
    )

    # basic processing in lizard
    sim_api.simulations_results_post_processing_lizard_basic_create(simulation_pk=created_sim.id,
                                                                    data={'scenario_name': simulation_name,
                                                                          'process_basic_results': True})

    # start simulation
    sim_start = sim_api.simulations_actions_create(simulation_pk=created_sim.id, data={"name": "start"})
    status = sim_api.simulations_status_list(created_sim.id, async_req=False)
    print(status.name)
    previous_status_name = status.name
    while status.name != "finished":
        if status.name != previous_status_name:
            print(status.name)
            previous_status_name = status.name
        status = sim_api.simulations_status_list(created_sim.id, async_req=False)
        try:
            progress = sim_api.simulations_progress_list(created_sim.id, async_req=False)
            print("\r" + str(progress.percentage), end="")
        except openapi_client.exceptions.ApiException:
            pass
        time.sleep(.5)

time.sleep(0)
with open(deelgebieden_fn, "r") as deelgebieden:
    for deelgebied_line in deelgebieden:
        try:
            deelgebied = deelgebied_line.strip()
            print('Started ' + deelgebied)
            prepare_local_repository(deelgebied=deelgebied)
            rev_nr = commit_and_push(local_repo_dir=local_repo_dir,
                                      commit_message=deelgebied)
            simulate(revision_number=rev_nr,
                     inpy_max_wait_time=600,
                     simulation_name='your_model_70mm1u'.format(deelgebied),
                     rain_duration=3600,
                     rain_intensity=70,
                     simulation_duration=3600+3600
                     )
            simulate(revision_number=rev_nr,
                     inpy_max_wait_time=10,
                     simulation_name='your_model_90mm1u'.format(deelgebied),
                     rain_duration=3600,
                     rain_intensity=90,
                     simulation_duration=3600+3600
                     )
            simulate(revision_number=rev_nr,
                     inpy_max_wait_time=10,
                     simulation_name='your_model_160mm2u'.format(deelgebied),
                     rain_duration=7200,
                     rain_intensity=80,
                     simulation_duration=7200+3600
                     )
        except Exception as e:
            print('ERROR! {} failed!'.format(deelgebied))
            traceback.print_exc()
            continue

print('Finished!')
