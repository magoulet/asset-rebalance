#!/usr/bin/env python3

import aws_cdk as cdk

from asset_rebalance.asset_rebalance_stack import AssetRebalanceStack


app = cdk.App()
AssetRebalanceStack(app, "AssetRebalanceStack")

app.synth()
