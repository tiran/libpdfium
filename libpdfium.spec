
# https://pdfium.googlesource.com/pdfium branch
%global pdfium_build 7049

# Tag from git ls-remote --sort -version:refname --tags https://chromium.googlesource.com/chromium/src '*.*.7049.0'
# Dependencies from https://pdfium.googlesource.com/pdfium/+/refs/heads/chromium/7049/DEPS
# PDFium wants specific commits of abseil-cpp, fast_float, and Chromium build tools.
# gtest and test_fonts are testing-only dependencies.
%global build_revision 3dd73ffc3708962da298795d99f35fc06ed0defc
%global abseil_revision 221ee3ed3b032d5a82736613440664f9fbe4d3db
%global fast_float_revision cb1d42aaa1e14b09e1452cfdef373d051b8c02a4
%global gtest_revision e235eb34c6c4fed790ccdad4b16394301360dcd4
%global test_fonts_revision 7f51783942943e965cd56facf786544ccfc07713
%global chromium_tag 135.0.7049.0


Name:           libpdfium
Version:        %{pdfium_build}
Release:        1%{?dist}
Summary:        Library for PDF rendering, inspection, manipulation and creation

License:        Apache 2.0
URL:            https://pdfium.googlesource.com/pdfium
# without testing/resources/pixel/bug_867501.pdf, test file is flagged as malicious content.
# Source0:        https://pdfium.googlesource.com/pdfium/+archive/refs/heads/chromium/%%{pdfium_build}.tar.gz#/pdfium-%%{pdfium_build}.tar.gz
Source0:        pdfium-%{pdfium_build}-clean.tar.gz
Source1:        https://chromium.googlesource.com/chromium/src/build.git/+archive/%{build_revision}.tar.gz#/build-%{build_revision}.tar.gz
Source2:        https://chromium.googlesource.com/chromium/src/third_party/abseil-cpp/+archive/%{abseil_revision}.tar.gz#/abseil-cpp-%{abseil_revision}.tar.gz
Source3:        https://chromium.googlesource.com/external/github.com/fastfloat/fast_float.git/+archive/%{fast_float_revision}.tar.gz#/fast_float-%{fast_float_revision}.tar.gz
Source4:        https://chromium.googlesource.com/external/github.com/google/googletest.git/+archive/%{gtest_revision}.tar.gz#/gtest-%{gtest_revision}.tar.gz
Source5:        https://chromium.googlesource.com/chromium/src/third_party/test_fonts.git/+archive/%{test_fonts_revision}.tar.gz#/test_fonts-%{test_fonts_revision}.tar.gz
Source6:        https://chromium.googlesource.com/chromium/src/+archive/refs/tags/%{chromium_tag}/tools/generate_shim_headers.tar.gz#/generate_shim_headers-%{chromium_tag}.tar.gz
Source10:       args.gn
Source11:       passflags-BUILD.gn


# fix for big endian bugs in CFX_SeekableStreamProxy code and BinaryBuffer tests
# https://issues.chromium.org/issues/402354437
Patch1:         0001-bigendian.patch
# OpenJPEG 2.4 support for RHEL 9
Patch2:         0002-openjpeg-2.4.patch

BuildRequires:  gcc-c++
BuildRequires:  glibc-devel
BuildRequires:  pkgconfig
BuildRequires:  redhat-rpm-config
BuildRequires:  libatomic
BuildRequires:  chrpath

BuildRequires:  gn
BuildRequires:  ninja-build

# unbundled dependencies
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libopenjp2)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(zlib)

# https://sourceforge.net/projects/agg/ 2.3 + security patches
Provides:       bundled(agg) = 2.3
Provides:       bundled(abseil-cpp) = %{abseil_revision}
Provides:       bundled(fast_float) = %{fast_float_revision}
Provides:       %{name}(chromium-tag) = %{chromium_tag}


%description
PDFium is a library for PDF rendering, inspection, manipulation and creation.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -qT -c -a 0 -n %{name}-%{version}
%setup -qT -c -a 1 -n %{name}-%{version}/build
%setup -qT -c -a 2 -n %{name}-%{version}/third_party/abseil-cpp
%setup -qT -c -a 3 -n %{name}-%{version}/third_party/fast_float/src
%setup -qT -c -a 4 -n %{name}-%{version}/third_party/googletest/src
%setup -qT -c -a 5 -n %{name}-%{version}/third_party/test_fonts
%setup -qT -c -a 6 -n %{name}-%{version}/tools/generate_shim_headers
# reset {_buildsubdir}
%setup -qTD -n %{name}-%{version}

%patch -P 1 -p1

%if 0%{?rhel} == 9
# RHEL 9 has OpenJPEG 2.4 without opj_decoder_set_strict_mode()
%patch -P 2 -p1
%endif

# Use relative paths in public/cpp headers
sed -i 's/"public\//\"..\//' public/cpp/*.h

# Unbundle ICU
mkdir -p third_party/icu
cp build/linux/unbundle/icu.gn third_party/icu/BUILD.gn

# Build static abseil-cpp
sed -i 's/component("absl")/static_library("absl")/' third_party/abseil-cpp/BUILD.gn

# Empty gclient config
touch build/config/gclient_args.gni

# Don't build test fonts, the fonts are required for embedded tests.
sed -i '/third_party\/test_fonts/d' testing/BUILD.gn

# Custom flavor of GCC toolchain that passes CFLAGS, CXXFLAGS, etc.
mkdir -p build/toolchain/linux/passflags
cp %{SOURCE11} build/toolchain/linux/passflags/BUILD.gn

# build configuration
mkdir -p out/release
cp %{SOURCE10} out/release/args.gn

# several test cases fail when compilers optimizes CFX_Matrix::GetInverse()
# with fused multiply-add (FMA) instructions. Disable floating-point
# expression contraction. Fixes: CFXMatrixTest.GetInverseCR702041,
# CPDFDocRenderDataTest.TransferFunctionOne, CPDFDocRenderDataTest.TransferFunctionArray
# https://issues.chromium.org/issues/402282789
%set_build_flags
export CPPFLAGS="-ffp-contract=off $CPPFLAGS"

# generate Ninja files with build flags
gn gen out/release


%build
# Build libpdfium.so and unit tests
%ninja_build -C out/release pdfium pdfium_unittests

# Remove rpath
chrpath --delete out/release/libpdfium.so

# Generate libpdfium pkgconfig file
cat > libpdfium.pc <<EOF
prefix=%{_prefix}
exec_prefix=%{_exec_prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: %{name}
Description: Library for PDF rendering, inspection, manipulation and creation
Version: %{version}
Cflags: -I\${includedir}
Requires.private: -lfreetype -licuuc -ljpeg -llcms2 -lopenjp2 -lz
Libs: -L\${libdir} -lpdfium
EOF


%check
%if 0%{?rhel} == 9
# RHEL 9: FlateModule.Encode fails because older zlib generates different result.
GTEST_FILTER="*-FlateModule.Encode"
%else
# run all tests
GTEST_FILTER="*"
%endif
GTEST_FILTER="$GTEST_FILTER" out/release/pdfium_unittests


%install
mkdir -p %{buildroot}%{_libdir}
cp out/release/libpdfium.so %{buildroot}%{_libdir}

mkdir -p %{buildroot}%{_includedir}/pdfium/cpp
cp public/*.h %{buildroot}%{_includedir}/pdfium
cp public/cpp/*.h %{buildroot}%{_includedir}/pdfium/cpp

mkdir -p %{buildroot}%{_libdir}/pkgconfig
cp libpdfium.pc %{buildroot}%{_libdir}/pkgconfig

%files
%license LICENSE
%doc AUTHORS out/release/args.gn
# pypdfium2 needs "libpdfium.so"
%{_libdir}/*.so

%files devel
%doc README.md
%{_includedir}/pdfium
%{_libdir}/pkgconfig/libpdfium.pc


%changelog
* Thu Mar 13 2025 Christian Heimes <cheimes@redhat.com> - 7049-1
- Update to PDFium 7049
- Rework build system
