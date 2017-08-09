#!/bin/bash -ex

test "$(curl 'https://localhost/hub/api' -k)" == '{"version": "0.7.2"}'
