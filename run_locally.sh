#!/bin/bash

cdk synth
sam local invoke -t cdk.out/AssetRebalanceStack.template.json -e ./events/apigw_event.json
