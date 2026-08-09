#! /bin/bash
set -euo pipefail

vips gaussblur pic.jpg "pic blur.jpg" 40
vips linear "pic blur.jpg" "pic blur dark.jpg" 0.9 0