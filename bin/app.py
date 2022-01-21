#!/usr/bin/env python3
import json
import sys
sys.path.append("./lib")

import aws_cdk as cdk
from pipeline_stack import PipelineStack

config_params = json.load(open("config.params.json", "r"))
app_name = config_params["Namespace"].replace("/", "")

app = cdk.App()
PipelineStack(app, app_name)

app.synth()
