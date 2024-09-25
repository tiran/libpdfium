# RPM package for PDFium (libpdfium)

1. `download-source.sh` creates a container image with Google's
   `depot_tools`, use `gclient` to fetch the sources, unbundles some third
   party packages, and finally creates a tar ball. The version is taken
   from `libpdfium.spec`
2. Two patches `public_headers.patch` and `shared_library.patch` from
   https://github.com/bblanchon/pdfium-binaries enable proper shared library
   builds as `libpdfium.so`.
3. `args.gn` compiles a release build with system packages and custom GCC
   build chain.
   > NOTE: OpenJPEG2 is currently too old to be used.
4. `passflags-BUILD.gn` defines custom GCC toolchain that passes C/CPP/CXX
   flags environment variables to the compiler. It's necessary to create a
   debug package.
