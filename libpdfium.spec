# for pypdfium2-4.30.0
%global tagversion 6462
# https://pdfium.googlesource.com/pdfium/+/refs/heads/chromium/6462
%global commit 7b7c83fba6d0af8d8847ee606569c35880512995
%global commitdate 20240502
%global shortcommit %(c=%{commit}; echo ${c:0:8})

%if 0%{?fedora} || 0%{?rhel} >= 10
%bcond_without openjpeg2
%else
# RHEL 9.4 has OpenJPEG2 2.4
%bcond_with openjpeg2
%endif

Name:           libpdfium
Version:        %{tagversion}^%{commitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Library for PDF rendering, inspection, manipulation and creation

License:        Apache 2.0
URL:            https://pdfium.googlesource.com/pdfium
Source0:        libpdfium-%{tagversion}.tar.gz
Source1:        args.gn
Source2:        passflags-BUILD.gn

# patches to use public headers, export public names, and to build libpdfium.so
# https://github.com/bblanchon/pdfium-binaries/tree/chromium/6721/patches
Patch1:         public_headers.patch
Patch2:         shared_library.patch

BuildRequires:  gcc-c++
BuildRequires:  glibc-devel
BuildRequires:  pkgconfig
BuildRequires:  redhat-rpm-config
BuildRequires:  libatomic

BuildRequires:  gn
BuildRequires:  ninja-build

# de-vendored dependencies
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libjpeg)
%if %{with openjpeg2}
BuildRequires:  pkgconfig(libopenjp2) >= 2.5
%endif
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(zlib)

# https://sourceforge.net/projects/agg/ 2.3 + security patches
Provides:       bundled(agg) = 2.3
%if %{without openjpeg2}
# OpenJPEG2 2.5.0 + security fixes
Provides:       bundled(openjpeg2) = 2.5.0
%endif
Provides:       bundled(abseil-cpp)


%description
Library for PDF rendering, inspection, manipulation and creation

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%autosetup -p1 -n libpdfium-%{tagversion}

# build configuration
install -D -m=644 %{SOURCE1} out/args.gn
%if %{with openjpeg2}
echo "use_system_libopenjpeg2 = true" >> out/args.gn
%else
echo "use_system_libopenjpeg2 = false" >> out/args.gn
%endif

# custom flavor of GCC toolchain that passes CFLAGS, CXXFLAGS, etc.
install -D -m=644 %{SOURCE2} build/toolchain/linux/passflags/BUILD.gn

# generate Ninja files with build flags
%set_build_flags
# build system does not define macro for some dependencies
export CPPFLAGS="-DUSE_SYSTEM_LCMS2=1 $CPPFLAGS"
gn gen out


%build
%ninja_build -C out pdfium


%install
mkdir -p %{buildroot}%{_libdir}
cp out/libpdfium.so %{buildroot}%{_libdir}

mkdir -p %{buildroot}%{_includedir}
cp public/*.h %{buildroot}%{_includedir}

%files
%license LICENSE
%doc AUTHORS out/args.gn
# PDFium build system does not include a soname
# pypdfium2 needs "libpdfium.so"
%{_libdir}/*.so

%files devel
%doc README.md
%{_includedir}/*


%changelog
* Mon Sep 30 2024 Christian Heimes <cheimes@redhat.com> - 6462^20240502git7b7c83fb-2
- use OpenJPEG2 on Fedora and EL10

* Fri Sep 27 2024 Christian Heimes <cheimes@redhat.com> - 6462^20240502git7b7c83fb-1
- Build tag 6462 for pypdfium2-4.30.0
