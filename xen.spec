# -*- rpm-spec -*-

# Commitish for Source0, required by tooling.
%global package_srccommit RELEASE-4.19.1

# Hypervisor release.  Should match the tag in the repository and would be in
# the Release field if it weren't for the %%{xsrel} automagic.
%global hv_rel 1

# Full hash from the HEAD commit of this repo during processing, usually
# provided by the environment.  Default to ??? if not set.
%{!?package_speccommit: %global package_speccommit ???}

# Normally derived from the tag and provided by the environment.  May be a
# `git describe` when not building an from a tagged changeset.
%{!?xsrel: %global xsrel %{hv_rel}}

%define base_dir  %{name}-%{version}

%define lp_devel_dir %{_usrsrc}/xen-%{version}-%{release}

# Prevent RPM adding Provides/Requires to lp-devel package, or mangling shebangs
%global __provides_exclude_from ^%{lp_devel_dir}/.*$
%global __requires_exclude_from ^%{lp_devel_dir}/.*$
%global __brp_mangle_shebangs_exclude_from ^%{lp_devel_dir}/.*$

%if 0%{?xenserver} < 9
%global __patch /usr/bin/patch --fuzz=0
%endif

Summary: Xen is a virtual machine monitor
Name:    xen
Version: 4.19.1
Release: %{?xsrel}%{?dist}
License: GPLv2 and LGPLv2 and MIT and Public Domain
URL:     https://www.xenproject.org
Source0: https://code.citrite.net/rest/archive/latest/projects/XSU/repos/%{name}/archive?at=%{package_srccommit}&prefix=%{base_dir}&format=tar.gz#/%{base_dir}.tar.gz
Source1: sysconfig_kernel-xen
Source2: xl.conf
Source3: logrotate-xen-tools
Source5: gen_test_metadata.py

ExclusiveArch: x86_64

BuildRequires: python3-devel
BuildRequires: python3-rpm-macros
%global py_sitearch %{python3_sitearch}
%global __python %{__python3}

%if 0%{?xenserver} < 9
# Interim, build Python2 bindings too
%global py2_compat 1
BuildRequires: python2-devel
BuildRequires: python2-rpm-macros
%endif

# These build dependencies are needed for building the xen.gz as
# well as live patches.
%define core_builddeps() %{lua:
    if tonumber(rpm.expand("0%{?xenserver}")) < 9 then
        deps = {
            'devtoolset-11-binutils',
            'devtoolset-11-gcc'
        }
    else
        deps = {
            'binutils',
            'gcc'
        }
    end

    -- For the banner
    table.insert(deps, 'figlet')

    -- For Kconfig
    table.insert(deps, 'bison')
    table.insert(deps, 'flex')

    for _, dep in ipairs(deps) do
        print(rpm.expand("%1") .. ': ' .. dep .. '\\n')
    end
}

%if 0%{?xenserver} < 9
%global _devtoolset_enable source /opt/rh/devtoolset-11/enable
%endif

%{core_builddeps BuildRequires}

BuildRequires: libtool

# For libxenguest (domain builder)
BuildRequires: bzip2-devel
BuildRequires: libzstd-devel
BuildRequires: lzo-devel
BuildRequires: xz-devel
BuildRequires: zlib-devel

# For libxl
BuildRequires: yajl-devel
BuildRequires: libuuid-devel
BuildRequires: perl-interpreter

# For libacpi
BuildRequires: iasl

# For libxenfsimage
BuildRequires: e2fsprogs-devel
BuildRequires: libblkid-devel

# For xentop
BuildRequires: ncurses-devel

# For RomBIOS
BuildRequires: dev86

# For ocaml components
BuildRequires: ocaml >= 4.13.1-3
BuildRequires: ocaml-findlib

# For manpages
BuildRequires: perl-podlators

# For xenguest
BuildRequires: json-c-devel
BuildRequires: libempserver-devel

%if 0%{?xenserver} < 9
BuildRequires: systemd
%else
BuildRequires: systemd-rpm-macros
%endif

# Need cov-analysis if coverity is enabled
%{?_cov_buildrequires}

%description
Xen Hypervisor.

%package hypervisor
Summary: The Xen Hypervisor
License: GPLv2
Requires(post): coreutils grep
%description hypervisor
This package contains the Xen Project Hypervisor combined with the XenServer patchqueue.

%package hypervisor-debuginfo
Summary: The Xen Hypervisor debug information
License: GPLv2
%description hypervisor-debuginfo
This package contains the Xen Hypervisor debug information.

%package tools
Summary: Xen Hypervisor general tools
License: GPLv2 and LGPLv2
Requires: xen-libs = %{version}
%description tools
This package contains the Xen Hypervisor general tools for all domains.

%package devel
Summary: The Xen Hypervisor public headers
License: MIT and Public Domain
%description devel
This package contains the Xen Hypervisor public header files.

%package libs
Summary: Xen Hypervisor general libraries
License: LGPLv2
%description libs
This package contains the Xen Hypervisor general libraries for all domains.

%package libs-devel
Summary: Xen Hypervisor general development libraries
License: LGPLv2
Requires: xen-libs = %{version}
Requires: xen-devel = %{version}
%description libs-devel
This package contains the Xen Hypervisor general development for all domains.

%package dom0-tools
Summary: Xen Hypervisor Domain 0 tools
License: GPLv2 and LGPLv2 and MIT
Requires: xen-dom0-libs = %{version}
Requires: xen-tools = %{version}
Obsoletes: xen-installer-files <= 4.13.5-10.42
Requires: edk2
Requires: ipxe
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%description dom0-tools
This package contains the Xen Hypervisor control domain tools.

%package dom0-libs
Summary: Xen Hypervisor Domain 0 libraries
License: GPLv2 and LGPLv2 and MIT
Requires: xen-hypervisor = %{version}
Obsoletes: xen-installer-files <= 4.13.5-10.42
%description dom0-libs
This package contains the Xen Hypervisor control domain libraries.

%package dom0-libs-devel
Summary: Xen Hypervisor Domain 0 headers
License: GPLv2 and LGPLv2 and MIT
Requires: xen-devel = %{version}
Requires: xen-dom0-libs = %{version}
%description dom0-libs-devel
This package contains the Xen Hypervisor control domain headers.

%package ocaml-libs
Summary: Xen Hypervisor ocaml libraries
License: LGPLv2
Requires: xen-dom0-libs = %{version}
%description ocaml-libs
This package contains the Xen Hypervisor ocaml libraries.

%package ocaml-devel
Summary: Xen Hypervisor ocaml headers
License: LGPLv2
Requires: xen-ocaml-libs = %{version}
Requires: xen-dom0-libs-devel = %{version}
%description ocaml-devel
This package contains the Xen Hypervisor ocaml headers.

%package dom0-tests
Summary: Xen Hypervisor tests
License: GPLv2
%description dom0-tests
This package contains test cases for the Xen Hypervisor.

%package lp-devel_%{version}_%{release}
License: GPLv2
Summary: Development package for building livepatches
%{core_builddeps Requires}
%description lp-devel_%{version}_%{release}
Contains the prepared source files, config, and xen-syms for building live
patches against base version %{version}-%{release}.

%prep
%autosetup -p1
%{?_cov_prepare}
%{?_coverity:cp misc/coverity/nodefs.h %{_cov_dir}/config/user_nodefs.h}
%{?_cov_make_model:%{_cov_make_model misc/coverity/model.c}}

base_cset=$(sed -ne 's/Changeset: \(.*\)/\1/p' < .gitarchive-info)
pq_cset="%{package_speccommit}"
echo "${base_cset:0:12}, pq ${pq_cset:0:12}" > .scmversion

%build

%{?_devtoolset_enable}
export XEN_TARGET_ARCH=%{_arch}
export PYTHON="%{__python}"

%configure --disable-qemu-traditional \
           --disable-seabios \
           --disable-stubdom \
           --disable-xsmpolicy \
           --disable-pvshim \
           --enable-rombios \
           --enable-systemd \
           --with-xenstored=oxenstored \
           --with-system-qemu=%{_libdir}/xen/bin/qemu-system-i386 \
           --with-system-ipxe=/usr/share/ipxe/ipxe.bin \
           --with-system-ovmf=/usr/share/edk2/OVMF-release.fd

# Take a snapshot of the configured source tree for livepatches
mkdir ../livepatch-src
cp -a . ../livepatch-src/
echo %{?_devtoolset_enable} > ../livepatch-src/prepare-build

# Build tools and man pages
%{?_cov_wrap} %{make_build} build-tools
%{make_build} -C docs man-pages

%if 0%{?py2_compat}
# Interim python2 bindings too
%{make_build} DESTDIR=%{buildroot} PYTHON=python2 -C tools/python
%{make_build} DESTDIR=%{buildroot} PYTHON=python2 -C tools/pygrub
%endif

# The hypervisor build system can't cope with RPM's {C,LD}FLAGS
unset CFLAGS
unset LDFLAGS

build_xen () { # $1=vendorversion $2=buildconfig $3=outdir $4=cov
    local mk ver cov

    [ -n "$1" ] && ver="XEN_VENDORVERSION=$1"
    [ -n "$4" ] && cov="%{?_cov_wrap}"

    mk="$cov %{make_build} -C xen $ver O=$3"

    mkdir xen/$3 && cp -a buildconfigs/$2 xen/$3/.config
    $mk olddefconfig
    $mk build MAP
}

# Builds of Xen
build_xen -%{hv_rel}   config-release         build-xen-release
build_xen -%{hv_rel}-d config-debug           build-xen-debug      cov
build_xen ""           config-pvshim          build-shim


%install

%{?_devtoolset_enable}
export XEN_TARGET_ARCH=%{_arch}
export PYTHON="%{__python}"

# The existence of this directory causes ocamlfind to put things in it
mkdir -p %{buildroot}%{_libdir}/ocaml/stublibs

%if 0%{?py2_compat}
# Interim python2 bindings.  Must be installed ahead of the main install-tools
# so the Python3 scripts take priority.
%{make_build} DESTDIR=%{buildroot} PYTHON=python2 install -C tools/python
%{make_build} DESTDIR=%{buildroot} PYTHON=python2 install -C tools/pygrub
%endif

# Install tools and man pages
%{make_build} DESTDIR=%{buildroot} install-tools
%{make_build} DESTDIR=%{buildroot} -C docs install-man-pages

# Install artefacts for livepatches
%{__install} -p -D -m 644 xen/build-xen-release/xen-syms %{buildroot}%{lp_devel_dir}/xen-syms
%{__install} -p -D -m 644 xen/build-xen-debug/xen-syms %{buildroot}%{lp_devel_dir}/xen-syms-d
cp -a ../livepatch-src/. %{buildroot}%{lp_devel_dir}

# Install release & debug Xen
install_xen () { # $1=vendorversion $2=outdir
    %{__install} -p -D -m 644 xen/$2/xen.gz     %{buildroot}/boot/xen-%{version}$1.gz
    %{__install} -p -D -m 644 xen/$2/System.map %{buildroot}/boot/xen-%{version}$1.map
    %{__install} -p -D -m 644 xen/$2/.config    %{buildroot}/boot/xen-%{version}$1.config
    %{__install} -p -D -m 644 xen/$2/xen-syms   %{buildroot}/boot/xen-syms-%{version}$1
}
install_xen -%{hv_rel}   build-xen-release
install_xen -%{hv_rel}-d build-xen-debug

# Install release shim
%{__install} -p -D -m 644 xen/build-shim/xen      %{buildroot}%{_libexecdir}/%{name}/boot/xen-shim
%{__install} -p -D -m 644 xen/build-shim/xen-syms %{buildroot}%{_libexecdir}/%{name}/boot/xen-shim-syms

# Build test case metadata
%{__python} %{SOURCE5} -i %{buildroot}%{_libexecdir}/%{name} -o %{buildroot}%{_datadir}/xen-dom0-tests-metadata.json

%{__install} -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/kernel-xen
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/xen/xl.conf
%{__install} -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/xen-tools
%{?_cov_install}

%files hypervisor
/boot/%{name}-%{version}-%{hv_rel}.gz
/boot/%{name}-%{version}-%{hv_rel}.map
/boot/%{name}-%{version}-%{hv_rel}.config
/boot/%{name}-%{version}-%{hv_rel}-d.gz
/boot/%{name}-%{version}-%{hv_rel}-d.map
/boot/%{name}-%{version}-%{hv_rel}-d.config
%config %{_sysconfdir}/sysconfig/kernel-xen
%license COPYING
%ghost %attr(0644,root,root) %{_sysconfdir}/sysconfig/kernel-xen-args

%files hypervisor-debuginfo
/boot/%{name}-syms-%{version}-%{hv_rel}
/boot/%{name}-syms-%{version}-%{hv_rel}-d
%{_libexecdir}/%{name}/boot/xen-shim-syms

%files tools
%{_bindir}/xenstore
%{_bindir}/xenstore-chmod
%{_bindir}/xenstore-control
%{_bindir}/xenstore-exists
%{_bindir}/xenstore-list
%{_bindir}/xenstore-ls
%{_bindir}/xenstore-read
%{_bindir}/xenstore-rm
%{_bindir}/xenstore-watch
%{_bindir}/xenstore-write

%files devel
%{_includedir}/%{name}/COPYING
%{_includedir}/%{name}/arch-arm.h
%{_includedir}/%{name}/arch-arm/hvm/save.h
%{_includedir}/%{name}/arch-arm/smccc.h
%{_includedir}/%{name}/arch-ppc.h
%{_includedir}/%{name}/arch-riscv.h
%{_includedir}/%{name}/arch-x86/cpuid.h
%{_includedir}/%{name}/arch-x86/cpufeatureset.h
%{_includedir}/%{name}/arch-x86/guest-acpi.h
%{_includedir}/%{name}/arch-x86/hvm/save.h
%{_includedir}/%{name}/arch-x86/hvm/start_info.h
%{_includedir}/%{name}/arch-x86/pmu.h
%{_includedir}/%{name}/arch-x86/xen-mca.h
%{_includedir}/%{name}/arch-x86/xen-x86_32.h
%{_includedir}/%{name}/arch-x86/xen-x86_64.h
%{_includedir}/%{name}/arch-x86/xen.h
%{_includedir}/%{name}/arch-x86_32.h
%{_includedir}/%{name}/arch-x86_64.h
%{_includedir}/%{name}/argo.h
%{_includedir}/%{name}/callback.h
%{_includedir}/%{name}/device_tree_defs.h
%{_includedir}/%{name}/dom0_ops.h
%{_includedir}/%{name}/domctl.h
%{_includedir}/%{name}/elfnote.h
%{_includedir}/%{name}/errno.h
%{_includedir}/%{name}/event_channel.h
%{_includedir}/%{name}/features.h
%{_includedir}/%{name}/foreign/arm32.h
%{_includedir}/%{name}/foreign/arm64.h
%{_includedir}/%{name}/foreign/x86_32.h
%{_includedir}/%{name}/foreign/x86_64.h
%{_includedir}/%{name}/grant_table.h
%{_includedir}/%{name}/hvm/dm_op.h
%{_includedir}/%{name}/hvm/e820.h
%{_includedir}/%{name}/hvm/hvm_info_table.h
%{_includedir}/%{name}/hvm/hvm_op.h
%{_includedir}/%{name}/hvm/hvm_vcpu.h
%{_includedir}/%{name}/hvm/hvm_xs_strings.h
%{_includedir}/%{name}/hvm/ioreq.h
%{_includedir}/%{name}/hvm/params.h
%{_includedir}/%{name}/hvm/pvdrivers.h
%{_includedir}/%{name}/hvm/save.h
%{_includedir}/%{name}/hypfs.h
%{_includedir}/%{name}/io/9pfs.h
%{_includedir}/%{name}/io/blkif.h
%{_includedir}/%{name}/io/cameraif.h
%{_includedir}/%{name}/io/console.h
%{_includedir}/%{name}/io/displif.h
%{_includedir}/%{name}/io/fbif.h
%{_includedir}/%{name}/io/fsif.h
%{_includedir}/%{name}/io/kbdif.h
%{_includedir}/%{name}/io/libxenvchan.h
%{_includedir}/%{name}/io/netif.h
%{_includedir}/%{name}/io/pciif.h
%{_includedir}/%{name}/io/protocols.h
%{_includedir}/%{name}/io/pvcalls.h
%{_includedir}/%{name}/io/ring.h
%{_includedir}/%{name}/io/sndif.h
%{_includedir}/%{name}/io/tpmif.h
%{_includedir}/%{name}/io/usbif.h
%{_includedir}/%{name}/io/vscsiif.h
%{_includedir}/%{name}/io/xenbus.h
%{_includedir}/%{name}/io/xs_wire.h
%{_includedir}/%{name}/kexec.h
%{_includedir}/%{name}/memory.h
%{_includedir}/%{name}/nmi.h
%{_includedir}/%{name}/physdev.h
%{_includedir}/%{name}/platform.h
%{_includedir}/%{name}/pmu.h
%{_includedir}/%{name}/pv-iommu.h
%{_includedir}/%{name}/sched.h
%{_includedir}/%{name}/sys/evtchn.h
%{_includedir}/%{name}/sys/gntalloc.h
%{_includedir}/%{name}/sys/gntdev.h
%{_includedir}/%{name}/sys/privcmd.h
%{_includedir}/%{name}/sys/xenbus_dev.h
%{_includedir}/%{name}/sysctl.h
%{_includedir}/%{name}/tmem.h
%{_includedir}/%{name}/trace.h
%{_includedir}/%{name}/vcpu.h
%{_includedir}/%{name}/version.h
%{_includedir}/%{name}/vm_event.h
%{_includedir}/%{name}/xen-compat.h
%{_includedir}/%{name}/xen.h
%{_includedir}/%{name}/xencomm.h
%{_includedir}/%{name}/xenoprof.h
%{_includedir}/%{name}/xsm/flask_op.h

%files libs
%{_libdir}/libxenevtchn.so.1
%{_libdir}/libxenevtchn.so.1.2
%{_libdir}/libxengnttab.so.1
%{_libdir}/libxengnttab.so.1.2
%{_libdir}/libxenstore.so.4
%{_libdir}/libxenstore.so.4.0
%{_libdir}/libxentoolcore.so.1
%{_libdir}/libxentoolcore.so.1.0
%{_libdir}/libxentoollog.so.1
%{_libdir}/libxentoollog.so.1.0
%{_libdir}/libxenvchan.so.4.19
%{_libdir}/libxenvchan.so.4.19.0

%files libs-devel

# Common
%{_includedir}/xen_list.h

# Lib Xen Evtchn
%{_includedir}/xenevtchn.h
%{_libdir}/libxenevtchn.a
%{_libdir}/libxenevtchn.so
%{_libdir}/pkgconfig/xenevtchn.pc

# Lib Xen Gnttab
%{_includedir}/xengnttab.h
%{_libdir}/libxengnttab.a
%{_libdir}/libxengnttab.so
%{_libdir}/pkgconfig/xengnttab.pc

# Lib XenStore
%{_includedir}/xenstore.h
%{_includedir}/xenstore_lib.h
%{_libdir}/libxenstore.a
%{_libdir}/libxenstore.so
%{_libdir}/pkgconfig/xenstore.pc
# Legacy XenStore header files, excluded to discourage their use
%exclude %{_includedir}/xs.h
%exclude %{_includedir}/xenstore-compat/xs.h
%exclude %{_includedir}/xs_lib.h
%exclude %{_includedir}/xenstore-compat/xs_lib.h

%{_includedir}/xentoolcore.h
%{_libdir}/libxentoolcore.a
%{_libdir}/libxentoolcore.so
%{_libdir}/pkgconfig/xentoolcore.pc

%{_includedir}/xentoollog.h
%{_libdir}/libxentoollog.a
%{_libdir}/libxentoollog.so
%{_libdir}/pkgconfig/xentoollog.pc

# Lib Xen Vchan
%{_includedir}/libxenvchan.h
%{_libdir}/libxenvchan.a
%{_libdir}/libxenvchan.so
%{_libdir}/pkgconfig/xenvchan.pc

%files dom0-tools
%{_sysconfdir}/bash_completion.d/xl
%exclude %{_sysconfdir}/rc.d/init.d/xencommons
%exclude %{_sysconfdir}/rc.d/init.d/xendomains
%exclude %{_sysconfdir}/rc.d/init.d/xendriverdomain
%exclude %{_sysconfdir}/sysconfig/xendomains
%exclude %{_sysconfdir}/rc.d/init.d/xen-watchdog
%config %{_sysconfdir}/logrotate.d/xen-tools
%config %{_sysconfdir}/sysconfig/xencommons
%config %{_sysconfdir}/xen/oxenstored.conf
%{_sysconfdir}/xen/scripts/block
%{_sysconfdir}/xen/scripts/block-common.sh
%{_sysconfdir}/xen/scripts/block-drbd-probe
%{_sysconfdir}/xen/scripts/block-dummy
%{_sysconfdir}/xen/scripts/block-enbd
%{_sysconfdir}/xen/scripts/block-iscsi
%{_sysconfdir}/xen/scripts/block-nbd
%{_sysconfdir}/xen/scripts/block-tap
%{_sysconfdir}/xen/scripts/colo-proxy-setup
%{_sysconfdir}/xen/scripts/external-device-migrate
%{_sysconfdir}/xen/scripts/hotplugpath.sh
%{_sysconfdir}/xen/scripts/launch-xenstore
%{_sysconfdir}/xen/scripts/locking.sh
%{_sysconfdir}/xen/scripts/logging.sh
%{_sysconfdir}/xen/scripts/vif-bridge
%{_sysconfdir}/xen/scripts/vif-common.sh
%{_sysconfdir}/xen/scripts/vif-nat
%{_sysconfdir}/xen/scripts/vif-openvswitch
%{_sysconfdir}/xen/scripts/vif-route
%{_sysconfdir}/xen/scripts/vif-setup
%{_sysconfdir}/xen/scripts/vscsi
%{_sysconfdir}/xen/scripts/xen-hotplug-common.sh
%{_sysconfdir}/xen/scripts/xen-network-common.sh
%{_sysconfdir}/xen/scripts/xen-script-common.sh
%exclude %{_sysconfdir}/%{name}/cpupool
%exclude %{_sysconfdir}/%{name}/README
%exclude %{_sysconfdir}/%{name}/xlexample.hvm
%exclude %{_sysconfdir}/%{name}/xlexample.pvhlinux
%exclude %{_sysconfdir}/%{name}/xlexample.pvlinux
%config %{_sysconfdir}/xen/xl.conf
%{_bindir}/vchan-socket-proxy
%{_bindir}/xen-cpuid
%{_bindir}/xen-detect
%{_bindir}/xenalyze
%{_bindir}/xencov_split

# Pygrub python libs
%{py_sitearch}/grub/
%{py_sitearch}/xenfsimage.cpython*.so
%{py_sitearch}/pygrub-0.7-py*.egg-info

%if 0%{?py2_compat}
%{python2_sitearch}/grub/
%{python2_sitearch}/xenfsimage.so
%{python2_sitearch}/pygrub-0.7-py*.egg-info
%endif

# Xen python libs
%{py_sitearch}/xen-3.0-py*.egg-info
%{py_sitearch}/xen/

%if 0%{?py2_compat}
%{python2_sitearch}/xen-3.0-py*.egg-info
%{python2_sitearch}/xen/
%endif

%{_libexecdir}/%{name}/bin/convert-legacy-stream
%{_libexecdir}/%{name}/bin/init-xenstore-domain
%{_libexecdir}/%{name}/bin/libxl-save-helper
%{_libexecdir}/%{name}/bin/lsevtchn
%{_libexecdir}/%{name}/bin/pygrub
%{_libexecdir}/%{name}/bin/readnotes
%{_libexecdir}/%{name}/bin/verify-stream-v2
%{_libexecdir}/%{name}/bin/xen-9pfsd
%{_libexecdir}/%{name}/bin/xen-init-dom0
%{_libexecdir}/%{name}/bin/xenconsole
%{_libexecdir}/%{name}/bin/xenctx
%{_libexecdir}/%{name}/bin/xendomains
%{_libexecdir}/%{name}/bin/xenguest
%{_libexecdir}/%{name}/bin/xenpaging
%{_libexecdir}/%{name}/boot/hvmloader
%{_libexecdir}/%{name}/boot/xen-shim
%{_sbindir}/flask-get-bool
%{_sbindir}/flask-getenforce
%{_sbindir}/flask-label-pci
%{_sbindir}/flask-loadpolicy
%{_sbindir}/flask-set-bool
%{_sbindir}/flask-setenforce
%{_sbindir}/gdbsx
%{_sbindir}/oxenstored
%{_sbindir}/xen-access
%{_sbindir}/xen-diag
%{_sbindir}/xen-hptool
%{_sbindir}/xen-hvmcrash
%{_sbindir}/xen-hvmctx
%{_sbindir}/xen-kdd
%{_sbindir}/xen-livepatch
%{_sbindir}/xen-lowmemd
%{_sbindir}/xen-mceinj
%{_sbindir}/xen-memshare
%{_sbindir}/xen-mfndump
%{_sbindir}/xen-spec-ctrl
%{_sbindir}/xen-ucode
%{_sbindir}/xen-vmdebug
%{_sbindir}/xen-vmtrace
%{_sbindir}/xenbaked
%{_sbindir}/xenconsoled
%{_sbindir}/xencov
%{_sbindir}/xenhypfs
%{_sbindir}/xenmon
%{_sbindir}/xenperf
%{_sbindir}/xenpm
%{_sbindir}/xenpmd
%{_sbindir}/xenstored
%{_sbindir}/xentop
%{_sbindir}/xentrace
%{_sbindir}/xentrace_setmask
%{_sbindir}/xentrace_setsize
%{_sbindir}/xenwatchdogd
%{_sbindir}/xl
%exclude %{_sbindir}/xenlockprof
%{_mandir}/man1/xenhypfs.1.gz
%{_mandir}/man1/xentop.1.gz
%{_mandir}/man1/xenstore-chmod.1.gz
%{_mandir}/man1/xenstore-ls.1.gz
%{_mandir}/man1/xenstore-read.1.gz
%{_mandir}/man1/xenstore-write.1.gz
%{_mandir}/man1/xenstore.1.gz
%{_mandir}/man1/xl.1.gz
%{_mandir}/man5/xl-disk-configuration.5.gz
%{_mandir}/man5/xl-network-configuration.5.gz
%{_mandir}/man5/xl-pci-configuration.5.gz
%{_mandir}/man5/xl.cfg.5.gz
%{_mandir}/man5/xl.conf.5.gz
%{_mandir}/man5/xlcpupool.cfg.5.gz
%{_mandir}/man7/xen-pci-device-reservations.7.gz
%{_mandir}/man7/xen-pv-channel.7.gz
%{_mandir}/man7/xen-tscmode.7.gz
%{_mandir}/man7/xl-numa-placement.7.gz
%exclude %{_mandir}/man7/xen-vtpm.7.gz
%exclude %{_mandir}/man7/xen-vtpmmgr.7.gz
%{_mandir}/man8/xentrace.8.gz
%{_mandir}/man8/xenwatchdogd.8.gz
%dir /var/lib/xen
%dir /var/log/xen
%{_unitdir}/proc-xen.mount
%{_unitdir}/xen-init-dom0.service
%{_unitdir}/xen-watchdog.service
%{_unitdir}/xenconsoled.service
%{_unitdir}/xenstored.service
%exclude %{_prefix}/lib/modules-load.d/xen.conf
%exclude %{_unitdir}/xen-qemu-dom0-disk-backend.service
%exclude %{_unitdir}/xendomains.service
%exclude %{_unitdir}/xendriverdomain.service

%files dom0-libs
%{_libdir}/libxencall.so.1
%{_libdir}/libxencall.so.1.3
%{_libdir}/libxenctrl.so.4.19
%{_libdir}/libxenctrl.so.4.19.0
%{_libdir}/libxendevicemodel.so.1
%{_libdir}/libxendevicemodel.so.1.4
%{_libdir}/libxenforeignmemory.so.1
%{_libdir}/libxenforeignmemory.so.1.4
%{_libdir}/libxenfsimage.so.4.19
%{_libdir}/libxenfsimage.so.4.19.0
%{_libdir}/libxenguest.so.4.19
%{_libdir}/libxenguest.so.4.19.0
%{_libdir}/libxenhypfs.so.1
%{_libdir}/libxenhypfs.so.1.0
%{_libdir}/libxenlight.so.4.19
%{_libdir}/libxenlight.so.4.19.0
%{_libdir}/libxenstat.so.4.19
%{_libdir}/libxenstat.so.4.19.0
%{_libdir}/libxlutil.so.4.19
%{_libdir}/libxlutil.so.4.19.0
%{_libdir}/xenfsimage/btrfs/fsimage.so
%{_libdir}/xenfsimage/ext2fs-lib/fsimage.so
%{_libdir}/xenfsimage/fat/fsimage.so
%{_libdir}/xenfsimage/iso9660/fsimage.so
%{_libdir}/xenfsimage/reiserfs/fsimage.so
%{_libdir}/xenfsimage/ufs/fsimage.so
%{_libdir}/xenfsimage/xfs/fsimage.so
%{_libdir}/xenfsimage/zfs/fsimage.so

%files dom0-libs-devel
%{_includedir}/xenfsimage.h
%{_includedir}/xenfsimage_grub.h
%{_includedir}/xenfsimage_plugin.h
%{_libdir}/libxenfsimage.so

%{_includedir}/xencall.h
%{_libdir}/libxencall.a
%{_libdir}/libxencall.so
%{_libdir}/pkgconfig/xencall.pc

%{_includedir}/xenctrl.h
%{_includedir}/xenctrl_compat.h
%{_libdir}/libxenctrl.a
%{_libdir}/libxenctrl.so
%{_libdir}/pkgconfig/xencontrol.pc

%{_includedir}/xendevicemodel.h
%{_libdir}/libxendevicemodel.a
%{_libdir}/libxendevicemodel.so
%{_libdir}/pkgconfig/xendevicemodel.pc

%{_includedir}/xenforeignmemory.h
%{_libdir}/libxenforeignmemory.a
%{_libdir}/libxenforeignmemory.so
%{_libdir}/pkgconfig/xenforeignmemory.pc

%{_includedir}/xenguest.h
%{_libdir}/libxenguest.a
%{_libdir}/libxenguest.so
%{_libdir}/pkgconfig/xenguest.pc

%{_includedir}/xenhypfs.h
%{_libdir}/libxenhypfs.a
%{_libdir}/libxenhypfs.so
%{_libdir}/pkgconfig/xenhypfs.pc

%{_includedir}/_libxl_types.h
%{_includedir}/_libxl_types_json.h
%{_includedir}/libxl.h
%{_includedir}/libxl_event.h
%{_includedir}/libxl_json.h
%{_includedir}/libxl_utils.h
%{_includedir}/libxl_uuid.h
%{_includedir}/libxlutil.h
%{_libdir}/libxenlight.a
%{_libdir}/libxenlight.so
%{_libdir}/libxlutil.a
%{_libdir}/libxlutil.so
%{_libdir}/pkgconfig/xenlight.pc
%{_libdir}/pkgconfig/xlutil.pc

%{_includedir}/xenstat.h
%{_libdir}/libxenstat.a
%{_libdir}/libxenstat.so
%{_libdir}/pkgconfig/xenstat.pc

%files ocaml-libs
%exclude %{_libdir}/ocaml/stublibs/dllxenbus_stubs.so
%exclude %{_libdir}/ocaml/stublibs/dllxenbus_stubs.so.owner
%{_libdir}/ocaml/stublibs/dllxenctrl_stubs.so
%{_libdir}/ocaml/stublibs/dllxenctrl_stubs.so.owner
%{_libdir}/ocaml/stublibs/dllxeneventchn_stubs.so
%{_libdir}/ocaml/stublibs/dllxeneventchn_stubs.so.owner
%{_libdir}/ocaml/stublibs/dllxenmmap_stubs.so
%{_libdir}/ocaml/stublibs/dllxenmmap_stubs.so.owner
%exclude %{_libdir}/ocaml/xenbus/META
%exclude %{_libdir}/ocaml/xenbus/xenbus.cma
%exclude %{_libdir}/ocaml/xenbus/xenbus.cmo
%{_libdir}/ocaml/xenctrl/META
%{_libdir}/ocaml/xenctrl/xenctrl.cma
%{_libdir}/ocaml/xeneventchn/META
%{_libdir}/ocaml/xeneventchn/xeneventchn.cma
%{_libdir}/ocaml/xenmmap/META
%{_libdir}/ocaml/xenmmap/xenmmap.cma
%exclude %{_libdir}/ocaml/xenstore/META
%exclude %{_libdir}/ocaml/xenstore/xenstore.cma
%exclude %{_libdir}/ocaml/xenstore/xenstore.cmo

%files ocaml-devel
%exclude %{_libdir}/ocaml/xenbus/libxenbus_stubs.a
%exclude %{_libdir}/ocaml/xenbus/xenbus.a
%exclude %{_libdir}/ocaml/xenbus/xenbus.cmi
%exclude %{_libdir}/ocaml/xenbus/xenbus.cmx
%exclude %{_libdir}/ocaml/xenbus/xenbus.cmxa
%{_libdir}/ocaml/xenctrl/libxenctrl_stubs.a
%{_libdir}/ocaml/xenctrl/xenctrl.a
%{_libdir}/ocaml/xenctrl/xenctrl.cmi
%{_libdir}/ocaml/xenctrl/xenctrl.cmx
%{_libdir}/ocaml/xenctrl/xenctrl.cmxa
%{_libdir}/ocaml/xeneventchn/libxeneventchn_stubs.a
%{_libdir}/ocaml/xeneventchn/xeneventchn.a
%{_libdir}/ocaml/xeneventchn/xeneventchn.cmi
%{_libdir}/ocaml/xeneventchn/xeneventchn.cmx
%{_libdir}/ocaml/xeneventchn/xeneventchn.cmxa
%{_libdir}/ocaml/xenmmap/libxenmmap_stubs.a
%{_libdir}/ocaml/xenmmap/xenmmap.a
%{_libdir}/ocaml/xenmmap/xenmmap.cmi
%{_libdir}/ocaml/xenmmap/xenmmap.cmx
%{_libdir}/ocaml/xenmmap/xenmmap.cmxa
%exclude %{_libdir}/ocaml/xenstore/xenstore.a
%exclude %{_libdir}/ocaml/xenstore/xenstore.cmi
%exclude %{_libdir}/ocaml/xenstore/xenstore.cmx
%exclude %{_libdir}/ocaml/xenstore/xenstore.cmxa

%files dom0-tests
%exclude %{_libexecdir}/%{name}/bin/depriv-fd-checker
%{_libexecdir}/%{name}/bin/test-cpu-policy
%{_libexecdir}/%{name}/bin/test-paging-mempool
%{_libexecdir}/%{name}/bin/test-resource
%{_libexecdir}/%{name}/bin/test-tsx
%{_libexecdir}/%{name}/bin/test-xenstore
%{_libexecdir}/%{name}/bin/test_x86_emulator
%{_datadir}/xen-dom0-tests-metadata.json

%files lp-devel_%{version}_%{release}
%{lp_devel_dir}

%doc

%post hypervisor
# Update the debug and release symlinks
ln -sf %{name}-%{version}-%{hv_rel}-d.gz /boot/xen-debug.gz
ln -sf %{name}-%{version}-%{hv_rel}.gz /boot/xen-release.gz

# Point /boot/xen.gz appropriately
if [ ! -e /boot/xen.gz ]; then
    # Use a production hypervisor by default
    ln -sf %{name}-%{version}-%{hv_rel}.gz /boot/xen.gz
elif [ ! -L /boot/xen.gz ]; then
    # Use the production hypervisor, but keep it unlinked
    cp -f /boot/%{name}-%{version}-%{hv_rel}.gz /boot/xen.gz
else
    # Else look at the current link, and whether it is debug
    path="`readlink -f /boot/xen.gz`"
    if [ ${path} != ${path%%-d.gz} ]; then
        ln -sf %{name}-%{version}-%{hv_rel}-d.gz /boot/xen.gz
    else
        ln -sf %{name}-%{version}-%{hv_rel}.gz /boot/xen.gz
    fi
fi

if [ -e %{_sysconfdir}/sysconfig/kernel ] && ! grep -q '^HYPERVISOR' %{_sysconfdir}/sysconfig/kernel ; then
  cat %{_sysconfdir}/sysconfig/kernel-xen >> %{_sysconfdir}/sysconfig/kernel
fi

%post dom0-tools
%systemd_post proc-xen.mount
%systemd_post var-lib-xenstored.mount
%systemd_post xen-init-dom0.service
%systemd_post xen-watchdog.service
%systemd_post xenconsoled.service
%systemd_post xenstored.service

%preun dom0-tools
%systemd_preun proc-xen.mount
%systemd_preun var-lib-xenstored.mount
%systemd_preun xen-init-dom0.service
%systemd_preun xen-watchdog.service
%systemd_preun xenconsoled.service
%systemd_preun xenstored.service

%postun dom0-tools
%systemd_postun proc-xen.mount
%systemd_postun var-lib-xenstored.mount
%systemd_postun xen-init-dom0.service
%systemd_postun xen-watchdog.service
%systemd_postun xenconsoled.service
%systemd_postun xenstored.service

%{?_cov_results_package}

%changelog
* Mon Feb 24 2025 Roger Pau Monné <roger.pau@citrix.com> - 4.19.1-2
- Fix (experimental) nested virt enabling
- Fix IO_PAGE_FAULT on AMD machines due to interrupt migration
- Reduce PCI config space accesses
- Fix reboot/shutdown issues on AMD due to local APIC ESR interrupts

* Mon Jan 13 2025 Andrew Cooper <andrew.cooper3@citrix.com> - 4.19.1-1
- Update to Xen 4.19.1

* Wed Dec 18 2024 Roger Pau Monné <roger.pau@citrix.com> - 4.17.5-7
- Fix IO-APIC initialization with ExtINT mode pins
- Fix emulation of MOVBE instruction
- Fix Ocaml rpath setting

* Tue Dec  3 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.5-6
- Fix migration of VMs from CH 8.2 CU1 to XS8 when the guest is using BHI_DIS_S

* Mon Nov 25 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.5-5
- Initial AMD Turin support
- Fix dom0 pIRQ limit calculation
- Fix emulation of BMI1/2 instructions

* Tue Nov  5 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.5-4
- Fixes for
  - XSA-463 CVE-2024-45818
  - XSA-464 CVE-2024-45819
- Fix IO-APIC directed EOIs when using AMD-Vi interrupt remapping
- Fix a crash during livepatch loading caused by an incorrect order of checks
- Switch xAPIC flat driver to use physical destination mode for external
  interrupts
- Remove an overly strict check when parsing AMD IVRS ACPI tables
- Fix a leak of pending interrupts during CPU offline

* Wed Sep 11 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.5-3
- Fix for XSA-462 CA-399169

* Tue Sep 10 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.5-2
- Fix x2APIC cluster handling across S3
- Avoid clobbering firmware memory during the load-base calculation
- Fix ASAN issues identified in `xentop` and `xl dmesg`

* Wed Aug 21 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.5-1
- Update to Xen 4.17.5

* Fri Aug  2 2024 Roger Pau Monné <roger.pau@citrix.com> - 4.17.4-8
- Fix for XSA-460 CVE-2024-31145
- Fix IO breakpoint recognition in PV guests
- Fix libxenstore.so to not modify SIGBUS behind the back of the application
- Fix a integer overflow in Xen's bunzip2(), leading to a rare decompression
  faliure

* Mon Jul 22 2024 Matthew Barnes <matthew.barnes@cloud.com> - 4.17.4-7
- Fix CLOEXEC handling in libxenstore
- Don't package Ocaml Xenbus library
- Inject #DF instead of overwriting RIP in xen-hvmcrash

* Wed Jul  3 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.4-6
- Fix for XSA-458 CVE-2024-31143
- Fix early detection of CPU features on hardware with the CPUID Limit active
  in firmware
- Fix a bug whereby dynamic XSTATE CPUID information was provided to all
  guests, even those with XSAVE disabled
- Fix a bug on Intel where HVM guests may have MMIO mappings forced to UC even
  if the guest kernel wanted a different cacheability
- Fix multiple bugs with interrupt affinity handling around CPU hotplug

* Fri May 31 2024 Pau Ruiz Safont <pau.ruizsafont@cloud.com> - 4.17.4-5
- Rebuild with OCaml 4.14.2 compiler.

* Thu May 30 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.4-4
- Don't link oxenstored against libsystemd, and remove systemd-devel as a
  build dependency
- Fix population of the online vCPU bitmap for PVH guests
- Drop unused openssl-devel build dependency

* Wed May 15 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.4-3
- Pass all MSI-X vector control writes to the device model
- Distinguish "ucode already up to date" and treat it as success
- Optimise HVMLoader AP bringup
- Fix xentop cpu% sort order
- Fix possible watchdog timeouts or NULL pointer deference with CPU hotplug

* Tue May  7 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.4-2
- Fix a heterogeneous CPU levelling bug between ICX and CLX

* Tue Apr 30 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.4-1
- Update to Xen 4.17.4
- Fix a bug in RTC emulation for HVM guests which occasionally causes OVMF to
  fail an assertion
- Fix a bug in livepatch application when CET-IBT is active, leading to a full
  host crash
- Include the debug xen debug symbols in in the lp-devel subpackage

* Tue Apr  9 2024 Alex Brett <alex.brett@cloud.com> - 4.17.3-6
- CA-391273: Rebuild to resolve xen-dom0-tools dependency issue

* Wed Apr  3 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.3-5
- Fixes for:
  - XSA-454 CVE-2023-46842
  - XSA-455 CVE-2024-31142
  - XSA-456 CVE-2024-2201

* Fri Mar  8 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.3-4
- Fixes for:
  - XSA-453 CVE-2024-2193, off by default
  - XSA-452 CVE-2023-28746
- Fix levelling of MD_CLEAR/FB_CLEAR across a pool
- Hide x2APIC from PV guests by default
- Fixes to livepatching, including the ability to patch .rodata
- Improve oxenstored performance by avoiding Hashtbl.copy when processing
  packets
- Print the SPECULATIVE_HARDEN_* options which are enabled at build time

* Fri Feb 23 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.3-3
- Fix for XSA-451 CVE-2023-46841.
- Fix the migration of VMs which had previously seen the CMP_LEGACY feature.
- Retire support to customise guest memory at the 1M boundary.

* Tue Feb 13 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.3-2
- De-virtualise more function pointers, based on boot time configuration
- Improve the performance of IOMMU construction for dom0
- Fix a bug with the determination of IVMD memory regions
- Fix inefficiencies with XEN_{SYS,DOM}CTL_getdomaininfo{,list}
- Fix undefined behaviour in compat_set_timer_op()
- Fix the Raw CPU Policy rescan when CPUID Masking is active

* Fri Jan 26 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.17.3-1
- Update to Xen 4.17
  Major highlights:
    - CET-SS, CET-IBT and IOMMU Superpages used on capable hardware
    - PV32, PV_LINEAR_PT and SHADOW_PAGING now compiled out
    - NX and HAP (Intel EPT or AMD NPT) support in hardware is now mandatory

* Wed Jan 24 2024 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.60
- Fix watchdog setup on Intel Sapphire Rapids and Emerald Rapids platforms.
- Adjust preemption during IOMMU setup to avoid triggering the watchdog.
- Extend AMD #1474 (crash after ~1044 days) workaround to Zen1 platforms.

* Tue Dec 19 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.59
- Enable AVX-512 by default for Intel IceLake and later CPUs.
- Rebuild with updated Ocaml 4.14 runtime.
- Fix possible memory leak in libxenguest cpu-policy infrastructure.

* Mon Dec 4 2023 Alejandro Vallejo <alejandro.vallejo@cloud.com> - 4.13.5-10.58
- Remove limit of 64 CPUs from hvmloader.
- Fix pygrub incompatibility with python3.
- Improve the livepatch infrastructure.

* Wed Nov 8 2023 Roger Pau Monné <roger.pau@citrix.com> - 4.13.5-10.57
- Add new x2APIC 'Mixed mode' driver, and use it by default.

* Wed Nov 1 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.56
- Fixes for
  - XSA-445 CVE-2023-46835
  - XSA-446 CVE-2023-46836

* Wed Nov 1 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.55
- Fix for AMD erratum #1485, which has been observed to cause #UD exception on
  AMD Zen4 systems.
- Allow using the platform/ovmf-override key to configure the OVMF firwmare to
  use on a per-VM basis.
- Further Python3 fixes.

* Tue Oct 17 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.54
- Increase the compile time max CPUs from 512 to 2048.

* Fri Sep 29 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.53
- Fixes for
  - XSA-438 CVE-2023-34322
  - XSA-440 CVE-2023-34323
  - XSA-442 CVE-2023-34326
  - XSA-443 CVE-2023-34325
  - XSA-444 CVE-2023-34327 CVE-2023-34328
- Pygrub extended to deprivilege itself before operating on guest disks.

* Tue Sep 19 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.52
- Fix for XSA-439 / CVE-2023-20588.
- Ignore MADT entries with invalid APIC_IDs.
- Fix the emulation of VPBLENDMW with a mask and memory operand.
- Fix a incorrect diagnostic about spurious interrupts.

* Fri Aug 25 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.51
- Further fix for XSA-433.  Extend the chicken-bit workaround to all CPUs
  which appear to be a Zen2 microarchtiecture, even those not on the published
  model list.
- Fix for AMD errata #1474.  Disable C6 after 1000 days of uptime on AMD Zen2
  systems to avoid a crash at ~1044 days.
- Fix for MSR_ARCH_CAPS boot-time calculations for PV guests.
- Remove the debug PV-shim hypervisor.  The release build is still present and
  operates as before.
- Remove TBOOT and XENOPROF support in Xen.  Both are obsolete and the latter
  leaves benign-but-alarming messages in logs.
- Remove the "pod" command line option.  This was intended as a further
  workaround for XSA-246, but wasn't effective owing to poor error handling
  elsewhere.

* Thu Aug 3 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.50
- Fixes for
  - XSA-434 CVE-2023-20569
  - XSA-435 CVE-2022-40982

* Thu Aug 3 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.49
- Fix bug in XSA-433 fix, which accidentally disabled a hardware errata
  workaround.
- Update IO-APIC IRTEs atomically.  Fixes a race condition which causes
  interrupts to be routed badly, often with "No irq handler for vector"
  errors.
- Expose MSR_ARCH_CAPS to guests on all Intel hardware by default.  On Cascade
  Lake and later hardware, guests now see the bits stating hardware immunity
  to various speculative vulnerabilities.

* Mon Jul 24 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.48
- Fix for XSA-433 CVE-2023-20593.
- Limit scheduler loadbalancing to once per millisecond.  This improves
  performance on large systems.
- Mask IO-APIC pins before enabling LVTERR/ESR.  This fixes issues booting if
  firmware leaves the IO-APIC in a bad state.

* Tue Jun 06 2023 Pau Ruiz Safont <pau.ruizsafont@cloud.com> - 4.13.5-10.47
- Backport late microcode loading changes.
- Rebuild with Ocaml 4.14.

* Fri May 19 2023 Roger Pau Monné <roger.pau@citrix.com> - 4.13.5-10.46
- Fix AMD-Vi assert.
- Remove broken not built code in pv-iommu.
- Add test_x86_emulator to XenDom0Tests.

* Thu May 11 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.45
- Ignore VCPU_SSHOTTMR_future entirely.  The only known user of this is Linux
  prior to v4.7, and the usage is buggy.  This resolves guest crashes during
  migration.
- Improve Xen's early boot checking of its own alignment.  In case of a
  bootloader error, this turns a crash with no diagnostics into a clear error
  message.
- Drop XENMEM_get_mfn_from_pfn technical debt, the use of which has been
  replaced by PV-IOMMU.
- Minor specfile improvements; branding, and a bad changelog date.

* Thu Apr 27 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.44
- Add Obsoletes following the removal of xen-installer-files.

* Mon Apr 17 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.43
- Remove the NR_IOMMUs compile time limit.  This is necessary to boot on
  4-socket Sapphire Rapids systems.
- Cope booting in x2APIC mode on AMD systems without XT mode.
- Allow creating domains with grant settings larger than dom0.
- Remove sequential microcode application support.  Only parallel application
  is supported by the HW vendors.
- Introduce an elfnote for Dom0 <-> Xen negotiation of the activation of
  PV-IOMMU.
- Increase the size of the serial transmit buffer.
- Backport python3 shebang fixes.  Drop obsolete scripts.
- Remove the xen-installer-files subpackage.  It was a vestigial remnant of an
  old build system.

* Mon Mar 6 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.42
- Fixes for
  - XSA-427 CVE-2022-42332
  - XSA-428 CVE-2022-42333 CVE-2022-42334
  - XSA-429 CVE-2022-42331
- Move partial python library from xen-tools to xen-dom0-tools.  The content
  was all specific to dom0, and ineligible to be used elsewhere.
- Reintroduce the python2 pygrub/libfsimage bindings.

* Fri Mar 3 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.41
- Load AMD microcode on all logical processors.
- Switch to using Python 3.  Retain Python 2 builds of xen.lowlevel in the
  short term until dependent packages have been updated.
- Fix libfsimage build in the presence of newer Linux headers.

* Mon Feb 6 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.40
- Fix for XSA-426 CVE-2022-27672.
- More fixes for memory corruption issues in the Ocaml bindings.
- On xenstored live update, validate the config file before launching
  into the new xenstored.

* Thu Feb 2 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.39
- Fix memory corruption issues in the Ocaml bindings.

* Mon Jan 16 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.5-10.38
- Update to Xen 4.13.5

* Fri Jan 13 2023 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.37
- Initial support for Intel Sapphire Rapids.
- Don't mark IRQ vectors as pending when the vLAPIC is disabled.  This fixes
  an issue with Linux 5.19 and later.
- Remove an incorrect but benign warning which occurs for a UEFI VM that
  modifies the vRTC time.
- Fix overflow with high frequency TSCs.
- Fix crash on boot with invalid UEFI framebuffer configurations.
- Fix race condition releasing an IRQ which is in the process of moving
  between CPUs.
- Fix timer affinity after S3.
- Drop Introspection Extensions.

* Fri Dec 2 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.36
- Activate AVX-512 by default on AMD platforms.
- Fixes for oxenstored live update.

* Fri Nov 4 2022  Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.35
- Fix for XSA-422 CVE-2022-23824

* Thu Oct 27 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.34
- Fixes for
  - XSA-326 CVE-2022-42311 CVE-2022-42312 CVE-2022-42313 CVE-2022-42314
            CVE-2022-42315 CVE-2022-42316 CVE-2022-42317 CVE-2022-42318
  - XSA-414 CVE-2022-42309
  - XSA-415 CVE-2022-42310
  - XSA-416 CVE-2022-42319
  - XSA-417 CVE-2022-42320
  - XSA-418 CVE-2022-42321
  - XSA-419 CVE-2022-42322 CVE-2022-42323
  - XSA-420 CVE-2022-42324
  - XSA-421 CVE-2022-42325 CVE-2022-42326

* Thu Oct 6 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.33
- Fixes for XSA-410 CVE-2022-33746, XSA-411 CVE-2022-33748.
- Activate DOITM (Data Operand Invariant Timing Mode) unilaterally on capable
  hardware (Intel IceLake/Gracemont and later) to keep properly-written crypto
  code safe from timing attacks.
- Fix compressed XSAVE size reporting.  Fixes an issue with Linux 5.19+ on
  Intel Skylake or AMD Zen1 or later hardware.
- Fix a performance issue when when using CUDA workloads (e.g. Tensorflow) on
  a passed-through GPU.

* Fri Sep 16 2022 Ross Lagerwall <ross.lagerwall@citrix.com> - 4.13.4-10.32
- Add TPM 2.0 supporting patches

* Wed Aug 17 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.31
- Fix CPU hotplug on AMD.
- Improve diagnostics in nmi_show_execution_state().
- Rework specfile so tools get the default RPM CFLAGS/LDFLAGS, including
  various hardening settings.

* Tue Aug 9 2022 Pau Ruiz Safont <pau.safont@citrix.com> - 4.13.4-10.30
- Bump release and rebuild with OCaml 4.13.1-3 compiler.

* Fri Aug 5 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.29
- Improve boot speed by using WC mappings for the VGA framebuffer.
- Fix crash on boot on AMD Zen2/3 systems when x2apic is disabled by firmware.
- Correct the RPM license fields.

* Tue Jul 26 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.28
- Fix for XSA-408 CVE-2022-33745.

* Fri Jul 8 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.27
- Fixes for XSA-407 CVE-2022-23816 CVE-2022-23825.
- Switch to x2APIC physical destination mode by default.  Addresses problems
  with vector exhaustion on large systems.
- Address an issue where EPT superpages were unnecessarily split.

* Thu Jun 16 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.26
- Fixes for XSA-404 CVE-2022-21123 CVE-2022-21125 CVE-2022-21166.

* Thu Jun 9 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.25
- Fixes for XSA-401 CVE-2022-26362, XSA-402 CVE-2022-26363 CVE-2022-26364.

* Wed Apr 13 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.24
- Rebuild using devtoolset-11.

* Wed Apr 13 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.23
- Fixes to the XSA-400 changes.

* Fri Mar 25 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.22
- Fixes for XSA-397 CVE-2022-26356, XSA-399 CVE-2022-26357, XSA-400
  CVE-2022-26358 CVE-2022-26359 CVE-2022-26360 CVE-2022-26361.

* Thu Mar 10 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.21
- Fix for XSA-386 CVE-2021-26401.

* Tue Feb 15 2022 Rob Hoes <rob.hoes@citrix.com> - 4.13.4-10.20
- Rebuild with OCaml 4.13.1 compiler.
- CP-37343: Drop Ocaml/CPUID technical debt.

* Tue Feb 8 2022 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-10.19
- Fixes for XSA-394 CVE-2022-23034, XSA-395 CVE-2022-23035.
- Support for AMD MSR_SPEC_CTRL in HVM guests.
- Logic to match the Intel Feb 2022 microcode.  De-featuring TSX on more
  client parts, and retrofitting AMD's PSFD interface for guests.
- Build fix for Ocaml 4.12
- Fix and simplify runtime new CPUID feature logic.

* Wed Dec 22 2021 Igor Druzhinin <igor.druzhinin@citrix.com> - 4.13.4-10.18
- CA-361938: Fix advertisment of HLE/RTM to guests on Broadwell
- CA-360592: CVE-2021-28705 / XSA-389: issues with partially successful
  P2M updates on x86
- CA-360591: CVE-2021-28704 / XSA-388: PoD operations on misaligned GFNs

* Tue Nov 02 2021 Igor Druzhinin <igor.druzhinin@citrix.com> - 4.13.4-10.17
- CP-38201: Enable static analysis with Coverity

* Wed Oct 13 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-3
- Fix ACPI table alignment in guests
- Fix compat hypercall translation
- Perf improvements at boot, for hypercalls, and for the XSM subsystem

* Wed Oct 6 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-2
- Fix boot failure if a PCI Bridge is has a subordinate bus of 255.
- Reduce overhead from the trace infrastructure.
- Fix for XSA-386 CVE-2021-28702.

* Fri Sep 10 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.4-1
- Update to RELEASE-4.13.4.

* Wed Sep 8 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.16
- Fix for XSA-384 CVE-2021-28701.
- Bugfixes to XSA-378 fix.

* Wed Sep 1 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.15
- Fixes for XSA-378 CVE-2021-28694 CVE-2021-28695 CVE-2021-28696, XSA-379
  CVE-2021-28697, XSA-380 CVE-2021-28698, XSA-382 CVE-2021-28699.
- Retain visibility of HLE/RTM CPUID bits in guests when resuming on a client
  part with TSX disabled.
- Use production hypervisor by default, rather than the debug hypervisor.

* Mon Aug 23 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.14
- Disable 32bit PV guests by default.  They're not security supported at all
  and by disabling them, we can recover performance in the common case from
  the Spectre mitigations.  If necessary, 32bit PV guests can be re-enabled by
  booting Xen with `pv=32`.

* Mon Jul 26 2021 Igor Druzhinin <igor.druzhinin@citrix.com> - 4.13.3-10.13
- Correctly handle IRQ > 255 on PCI passthrough
- Reserve HyperTransport region properly on AMD Fam 17h+
- More IOMMU error path fixes
- Fix populating vbd.rd_sect in xentop

* Wed Jul 21 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.12
- Remove old workaround which causes a test-tsx failure on the hardware which
  the Intel June microcode de-featured TSX on.

* Wed Jun 30 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.11
- Fix migration of VMs which previously saw MPX.

* Tue Jun 22 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.10
- New xen-dom0-tests subpackage with unit and low level functional tests.
- Logic to match the Intel June microcode, de-featuring TSX on client parts.
- Prep work to move CPUID handling out of xenopsd and into libxc.
- Hide MPX by default from VMs.

* Mon Jun 14 2021 Igor Druzhinin <igor.druzhinin@citrix.com> - 4.13.3-10.8
- Fix another race with vCPU timers

* Wed Jun 9 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.7
- LBR and PMU fixes for Icelake Server
- Don't assume that VT-d Register based invalidation is available.  Expected
  to be necessary to boot on Sapphire Rapids Server.
- Fix the emulation of the PINSRW instruction.
- Reduce lock contention for virtual periodic timers, to fix a perf regression
  introduced by the XSA-336 fix.
- Fixes for XSA-373 CVE-2021-28692, XSA-375 CVE-2021-0089 CVE-2021-26313,
  XSA-377 CVE-2021-28690.

* Fri Apr 16 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.6
- Fix booting on Intel systems with static PIT clock gating.
- Drop unnecessary build dependencies.

* Fri Mar 26 2021 Rob Hoes <rob.hoes@citrix.com> - 4.13.3-10.5
- Rebuild with OCaml 4.10 compiler.

* Tue Mar 23 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.3-10.4
- Update to Xen 4.13.3.

* Mon Mar 22 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.2-10.3
- Fix library packaging so that autoreqprov doesn't cause xen-libs{,-devel} to
  depend on xen-dom0-libs{,devel}.

* Fri Mar 12 2021 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.2-10.2
- Fix a failure to boot of Windows Server vNext (build 20270).  Reduces the
  upper limit of HVM vCPUs to 64, pending other bugfixes.
- Advertise Viridian vCPU hotplug to guests as Xen already implements the
  functionality.
- Fixes for XSA-360 CVE-2021-3308.
- Backport XEN_DMOP_nr_vcpus and stable library fixes.
- Backport build system fix and drop 32bit libc as a build dependency.
- Fix microcode loading on AMD Family 19h (Zen3) parts.
- Fix HVM Shadow / migrating PV guests on IceLake parts.
- Fix booting on IceLake when the IOMMU is left in a partially initialised
  state by the firmware.

* Fri Dec 18 2020 Andrew Cooper <andrew.cooper3@citrix.com> - 4.13.2-10.1
- Backport changes for Ocaml 4.10 compatibility
- Fixes for XSA-115 CVE-2020-29480, XSA-322 CVE-2020-29481, XSA-323
  CVE-2020-29482, XSA-324 CVE-2020-29484, XSA-325 CVE-2020-29483, XSA-330
  CVE-2020-29485, XSA-348 CVE-2020-29484, XSA-352 CVE-2020-29486, XSA-353
  CVE-2020-29479, XSA-359 CVE-2020-29571
- Prototype oxenstored live update support
