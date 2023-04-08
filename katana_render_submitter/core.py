import subprocess
import os
from datetime import datetime
import json

from Katana import NodegraphAPI, KatanaFile

from katana_render_submitter import util

#TODO in set shot context tool, make sure base paths exists like render_cg


def package_job(jobs, force_cloud):
    #TODO use this later
    shot_context = None
    # get katana file
    katana_scene = NodegraphAPI.GetProjectAssetID()
    file_name = katana_scene.split('/')[-1:][0].strip('.katana')
    # add nodes to katana graph for rendering
    clean_up_dict = dict()
    for job in jobs:
        # get render pass input port and connected node
        render_node = NodegraphAPI.GetNode(job.pass_name)
        node_pos = NodegraphAPI.GetNodePosition(render_node)
        new_pos = (node_pos[0], (node_pos[1] + 50))
        # create render output define node, and position above
        rod = NodegraphAPI.CreateNode('RenderOutputDefine', NodegraphAPI.GetRootNode())
        NodegraphAPI.SetNodePosition(rod, new_pos)
        # disconnect and connect new ports
        render_input_port = render_node.getInputPortByIndex(0)
        incoming_port = render_input_port.getConnectedPort(0)
        render_input_port.disconnect(incoming_port)
        incoming_port.connect(rod.getInputPort('input'))
        rod.getOutputPort('out').connect(render_input_port)
        # set output path for render
        rod.checkDynamicParameters()
        rod.getParameter('args.renderSettings.outputs.outputName.locationSettings.renderLocation.enable').setValue(True, 0)
        #job.get_render_path()
        rod.getParameter('args.renderSettings.outputs.outputName.locationSettings.renderLocation.value').setValue(job.render_output,0)
        clean_up_dict[rod] = (render_input_port, incoming_port)
    # save file and make a snapshot.
    KatanaFile.Save(katana_scene)
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    job_id = str(ts).split('.')[0]
    snapshot_file = '{}/tmp/{}_{}.katana'.format(jobs[0].shot_dir, file_name, job_id)
    subprocess.run(['cp', katana_scene, snapshot_file])
    # build data for render job
    data_dict = {'Job:{}'.format(job_id): list()}
    for job in jobs:
        #TODO format this multiline
        batch_command = ['{}/katana'.format(os.getenv('KATANA_ROOT')), '--batch', '_3DELIGHT_FORCE_CLOUD={}'.format(force_cloud), '--reuse-render-process', '--katana-file={}'.format(snapshot_file), '--t={}'.format(job.frame_range), '--render-node={}'.format(job.pass_name)]
        #TODO if rendering locally, want to remove cloud flags
        data_dict[next(iter(data_dict))].append({'batch_cmd': batch_command, 'pass_name': job.pass_name, 'frame_range': job.frame_label, 'version': job.version})
    # write out file to shot dir
    #TODO will need to be patched, put the shot context at the start of this function
    job_file = '{}/tmp/{}_{}.json'.format(jobs[0].shot_dir, file_name, job_id)
    out_file = open(job_file, 'w')
    json.dump(data_dict, out_file, indent=6)
    out_file.close()
    #clean up newely creates nodes
    for node, ports in clean_up_dict.items():
        node.delete()
        ports[1].connect(ports[0])
    KatanaFile.Save(katana_scene)


def camel_case_split(str):
    words = [[str[0]]]
    for c in str[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return [''.join(word) for word in words]



def get_renderpass_data():
    data_dict = dict()
    for render_node in NodegraphAPI.GetAllNodesByType('Render'):
        pass_name = render_node.getName()
        pass_name_split = camel_case_split(pass_name)
        category = pass_name_split[-1][:-2].lower()
        if category in data_dict:
            data_dict[category].append(pass_name)
        else:
            data_dict[category] = [pass_name]
    return data_dict


class Job(object):
    def __init__(self, pass_name, frame_range, version):
        self.pass_name = pass_name
        self.frame_range = str()
        self.frame_label = str()
        self.shot_range = '1121-1266'
        self.version = version
        #TODO these should do in an inherited module called JOB and each job should be a TASK...
        # self.show = os.getenv('SHOW')
        # self.scene = os.getenv('SCENE')
        # self.shot = os.getenv('SHOT')
        # self.shot_context = '{}/{}/{}'.format(self.show, self.scene, self.shot)
        self.shot_dir = '/tlg/shows/{}'.format(util.get_shot_context())
        self.render_output = str()
        #self.get_render_node()
        self.get_render_path()
        self.get_frame_range(frame_range)

    def get_render_path(self):
        self.render_dir = '{}/render_cg'.format(self.shot_dir)
        version = self.version_up(self.version)
        self.version = version
        #TODO should add sSCENE_SHOT into render file name
        self.render_output = '{}/{}/{}/{}_primary_#.exr'.format(
            self.render_dir,
            self.pass_name,
            version,
            self.pass_name
        )

    def get_frame_range(self, range):
        start, end = self.shot_range.split('-')
        start = int(start)
        end = int(end)
        if '-' in range:
            valid_range = range
            self.frame_label = valid_range
        elif range == 'FML':
            middle = str(round((start+end)/2))
            valid_range = f'{start},{middle},{end}'
            self.frame_label = valid_range
        elif range == 'x10':
            frames = '1121,1131,1141,1151,1161,1171,1181,1191,1201,1211,1221,1231,1241,1251,1261'
            #TODO this doesn't work, so need the above workaround
            #print (list(range(1121, 1266, 10)))
            #frames = range(start, end, 10)
            valid_range = frames
            self.frame_label = f'{self.shot_range}x10'

        self.frame_range = valid_range

    def version_up(self, version_type):
        pass_exists = True
        intended_pass = self.render_dir+'/'+self.pass_name
        if not os.path.exists(intended_pass):
            if version_type == 'V+':
                ver = 'v01'
            else:
                ver = version_type
            pass_version_path = f'{intended_pass}/{ver}'
            os.makedirs(pass_version_path)
            pass_exists = False
        # check version for existing directory
        latest_version = max(os.listdir(intended_pass))
        if not pass_exists:
            pass
        else:
            if version_type == 'V+':
                current_version = int(latest_version.split('v')[1])
                latest_version = 'v{:02d}'.format(current_version+1)
            else:
                latest_version = f'v{version_type}'
        return latest_version


# importlib.reload(core)
# x.get_render_path()
# x.version_up()


'''
import importlib
import threading
from katana_render_submitter import core
thread_function = core.launch_render_cmd
x = threading.Thread(target=thread_function, args=('1121',), daemon=False)
y = threading.Thread(target=thread_function, args=('1122',), daemon=False)
x.start()
y.start()
'''