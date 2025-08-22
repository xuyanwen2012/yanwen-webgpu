launch-server:
    uv run main.py

# This is for Intel Arc B580 on Linux
launch-chrome-unstable:
    google-chrome-unstable http://localhost:8001 \
    --enable-features=Vulkan,UseSkiaRenderer,DefaultANGLEVulkan \
    --use-vulkan=swiftshader:none \
    --ozone-platform=wayland \
    --enable-unsafe-webgpu --enable-webgpu-developer-features
   
launch-chrome:
    google-chrome http://localhost:8001 \
    --enable-unsafe-webgpu --enable-webgpu-developer-features
   
