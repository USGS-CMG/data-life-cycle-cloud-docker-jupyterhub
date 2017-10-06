#!/bin/bash -ex

echo "Testing server response"
test "$(curl 'https://localhost/hub/api' -k)" == '{"version": "0.8.0"}'
