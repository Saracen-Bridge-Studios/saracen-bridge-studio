The optional AI engine that Setup.exe installs when the user picks "Install Gemma" on the AI engine page.

Nothing here is packed into Setup.exe except the two licence notices. Everything else is downloaded during
installation only if the user chooses Gemma, and checked by Inno Setup against its SHA-256:

  llama.cpp server for Windows, release b11577, Vulkan build (NVIDIA, AMD and Intel graphics; CPU when there is
  none), the official release zip (32 MB, 91 MB unpacked), SHA-256
  1d9a92d7bd92d41ace1ac21fb3ac2241a8175b932b9229b0d54e8bf625df8a81, unpacked to <install folder>\llm

  Gemma 4 12B  google/gemma-4-12B-it-qat-q4_0-gguf  gemma-4-12b-it-qat-q4_0.gguf  6.98 GB
  Gemma 4 E4B  google/gemma-4-E4B-it-qat-q4_0-gguf  gemma-4-E4B_q4_0-it.gguf      5.15 GB
  Destination: <install folder>\llm\models. Upgrades keep it; uninstall removes it.

Silent installs: /GEMMA=12b | e4b | skip   (silent default: skip)

The app starts the server only when a writing tool first runs, on a free local port (never 8799), with thinking
off unless Deep reasoning is chosen, and stops it on exit. On Windows the server sits in a job object, so it also
stops if the Studio crashes or is killed.

LICENSE-Gemma.txt and LICENSE-llama.cpp.txt are kept in the source; they are installed with the engine.
