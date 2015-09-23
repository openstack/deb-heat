#!/usr/bin/env python
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Heat Engine Server.  This does the work of actually implementing the API
calls made by the user.  Normal communications is done via the heat API
which then calls into this engine.
"""

import eventlet
eventlet.monkey_patch()

import sys

from oslo_config import cfg
import oslo_i18n as i18n
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr
from oslo_service import service

from heat.common import config
from heat.common.i18n import _LC
from heat.common import messaging
from heat.common import profiler
from heat.engine import template
from heat.rpc import api as rpc_api
from heat import version

i18n.enable_lazy()

LOG = logging.getLogger('heat.engine')


def main():
    logging.register_options(cfg.CONF)
    cfg.CONF(project='heat', prog='heat-engine',
             version=version.version_info.version_string())
    logging.setup(cfg.CONF, 'heat-engine')
    logging.set_defaults()
    messaging.setup()

    config.startup_sanity_check()

    mgr = None
    try:
        mgr = template._get_template_extension_manager()
    except template.TemplatePluginNotRegistered as ex:
        LOG.critical(_LC("%s"), ex)
    if not mgr or not mgr.names():
        sys.exit("ERROR: No template format plugins registered")

    from heat.engine import service as engine  # noqa

    profiler.setup('heat-engine', cfg.CONF.host)
    gmr.TextGuruMeditation.setup_autorun(version)
    srv = engine.EngineService(cfg.CONF.host, rpc_api.ENGINE_TOPIC)
    launcher = service.launch(cfg.CONF, srv,
                              workers=cfg.CONF.num_engine_workers)
    if cfg.CONF.enable_cloud_watch_lite:
        # We create the periodic tasks here, which mean they are created
        # only in the parent process when num_engine_workers>1 is specified
        srv.create_periodic_tasks()
    launcher.wait()
