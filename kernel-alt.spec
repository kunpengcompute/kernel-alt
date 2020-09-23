# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

%global src_pkg_name kernel-alt
%global bin_pkg_name kernel
%global bin_suffix_name %{nil}

Summary: The Linux kernel

# % define buildid .local

# For a kernel released for public testing, released_kernel should be 1.
# For internal testing builds during development, it should be 0.
%global released_kernel 0

%global distro_build 115

%define rpmversion 4.14.0
%define pkgrelease 115.el7a

# allow pkg_release to have configurable %{?dist} tag
%define specrelease 115%{?dist}.0.2

%define pkg_release %{specrelease}%{?buildid}

# The kernel tarball/base version
%define rheltarball %{rpmversion}-%{pkgrelease}

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# kernel
%define with_default   %{?_without_default:   0} %{?!_without_default:   1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-kdump (only for s390x)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     0}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 0}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_with_kernel_abi_whitelists: 0} %{?!_with_kernel_abi_whitelists: 1}

# In RHEL, we always want the doc build failing to build to be a failure,
# which means settings this to false.
%define doc_build_fail false

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}

# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}

# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'. RHEL only ever does 1.
%define debugbuildsenabled 1

%define with_gcov %{?_with_gcov: 1} %{?!_with_gcov: 0}

# turn off debug kernel and kabichk for gcov builds
%if %{with_gcov}
%define with_debug 0
%define with_kabichk 0
%endif

%define make_target bzImage

# Kernel Version Release + Arch -> KVRA
%define KVRA %{version}-%{release}.%{_target_cpu}
%define hdrarch %{_target_cpu}
%define asmarch %{_target_cpu}
%define cross_target %{_target_cpu}

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_debug 0
%define with_kdump 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_default 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%endif

# These arches install vdso/ directories.
%define vdso_arches aarch64 ppc64le s390x x86_64

# Overrides for generic default options

# only build debug kernel on architectures below
%ifnarch aarch64 ppc64le s390x x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_kernel_abi_whitelists 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_default 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs %{src_pkg_name}-%{version}-*.config
%endif

# sparse blows up on ppc*
%ifarch ppc64 ppc64le ppc
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch aarch64
%define asmarch arm64
%define hdrarch arm64
%define all_arch_configs %{src_pkg_name}-%{version}-aarch64*.config
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%define image_install_path boot
%endif

%ifarch i686
%define asmarch x86
%define hdrarch i386
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs %{src_pkg_name}-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%endif

%ifarch ppc64 ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs %{src_pkg_name}-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_bootwrapper 1
%define cross_target powerpc64
%define kcflags -O3
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs %{src_pkg_name}-%{version}-s390x*.config
%define image_install_path boot
%define kernel_image arch/s390/boot/bzImage
%define with_tools 0
%define with_kdump 1
%endif

#cross compile make
%if %{with_cross}
%define cross_opts CROSS_COMPILE=%{cross_target}-linux-gnu-
%define with_perf 0
%define with_tools 0
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%define listnewconfig_fail 1

# We only build kernel headers package on the following, for being able to do
# builds with a different bit length (eg. 32-bit build on a 64-bit environment).
# Do not remove them from ExclusiveArch tag below
%define nobuildarches i686 ppc s390

%ifarch %nobuildarches
%define with_bootwrapper 0
%define with_default 0
%define with_debug 0
%define with_debuginfo 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs aarch64 ppc64le x86_64

%define zipmodules 1

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3, xfsprogs < 4.3.0, kmod < 20-9

# We moved the drm include files into kernel headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
%define initrd_prereq  dracut >= 033-283

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVRA}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20160615-46\
Requires(post): %{_sbindir}/new-kernel-pkg\
Requires(post): system-release\
Requires(preun): %{_sbindir}/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: %{src_pkg_name}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# Some architectures need a different headers version for user space builds with
# a different bit length environment (eg. 32-bit user space build on 64-bit).
# For architectures we support, where we must provide a compatible kernel-headers
# package, don't exclude them in ExclusiveArch below, but add them to
# %%nobuildarches (above) instead. Example: if we support x86_64, we must build
# the i686 (32-bit) headers and provide a package with them
ExclusiveArch: aarch64 i686 noarch ppc ppc64le s390 s390x x86_64
ExclusiveOS: Linux

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 4.8.5-29, binutils >= 2.12, redhat-rpm-config >= 9.1.0-55
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl openssl-devel
BuildRequires: hmaccalc
BuildRequires: python-devel, newt-devel, perl(ExtUtils::Embed)
BuildRequires: git
%ifarch x86_64
BuildRequires: pesign >= 0.109-4
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel bison
BuildRequires: audit-libs-devel
BuildRequires: java-devel
%ifnarch s390 s390x
BuildRequires: numactl-devel
%endif
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
%if %{with_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8/RHEL 6.
# The -r flag to find-debuginfo.sh invokes eu-strip --reloc-debug-sections
# which reduces the number of relocations in kernel module .ko.debug files and
# was introduced with rpm 4.9 and elfutils 0.153.
BuildRequires: rpm-build >= 4.9.0-1, elfutils >= 0.153-1
%define debuginfo_args --strict-build-id -r
%endif
%ifarch s390x
# required for zfcpdump
BuildRequires: glibc-static
%endif

Source0: linux-%{rpmversion}-%{pkgrelease}.tar.xz

Source1: Makefile.common

Source10: sign-modules
%define modsign_cmd %{SOURCE10}
Source11: x509.genkey
%if %{?released_kernel}
Source13: centos-ca-secureboot.der
Source14: centossecureboot001.crt
%define pesign_name centossecureboot001
%else
Source13: centos-ca-secureboot.der
Source14: centossecureboot001.crt
%define pesign_name centossecureboot001
%endif
Source15: centos-ldup.x509
Source16: centos-kpatch.x509

Source18: check-kabi

Source20: Module.kabi_x86_64
Source21: Module.kabi_ppc64le
Source22: Module.kabi_aarch64
Source23: Module.kabi_s390x

Source25: kernel-abi-whitelists-%{distro_build}.tar.bz2

Source50: %{src_pkg_name}-%{version}-x86_64.config
Source51: %{src_pkg_name}-%{version}-x86_64-debug.config

# Source60: %{src_pkg_name}-%{version}-ppc64.config
# Source61: %{src_pkg_name}-%{version}-ppc64-debug.config
Source62: %{src_pkg_name}-%{version}-ppc64le.config
Source63: %{src_pkg_name}-%{version}-ppc64le-debug.config

Source70: %{src_pkg_name}-%{version}-s390x.config
Source71: %{src_pkg_name}-%{version}-s390x-debug.config
Source72: %{src_pkg_name}-%{version}-s390x-kdump.config

Source80: %{src_pkg_name}-%{version}-aarch64.config
Source81: %{src_pkg_name}-%{version}-aarch64-debug.config

# Sources for kernel tools
Source2000: cpupower.service
Source2001: cpupower.config

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch
#Marvell Patches
Patch8001: 0001-net-mvpp2-remove-useless-goto.patch
Patch8002: 0002-net-mvpp2-set-the-Rx-FIFO-size-depending-on-the-port.patch
Patch8003: 0003-net-mvpp2-initialize-the-Tx-FIFO-size.patch
Patch8004: 0004-net-mvpp2-initialize-the-RSS-tables.patch
Patch8005: 0005-net-mvpp2-limit-TSO-segments-and-use-stop-wake-thres.patch
Patch8006: 0006-net-mvpp2-use-the-aggr-txq-size-define-everywhere.patch
Patch8007: 0007-net-mvpp2-simplify-the-Tx-desc-set-DMA-logic.patch
Patch8008: 0008-net-mvpp2-add-ethtool-GOP-statistics.patch
Patch8009: 0009-net-mvpp2-fix-GOP-statistics-loop-start-and-stop-con.patch
Patch8010: 0010-net-mvpp2-fix-the-txq_init-error-path.patch
Patch8011: 0011-net-mvpp2-cleanup-probed-ports-in-the-probe-error-pa.patch
Patch8012: 0012-net-mvpp2-do-not-disable-GMAC-padding.patch
Patch8013: 0013-net-mvpp2-check-ethtool-sets-the-Tx-ring-size-is-to-.patch
Patch8014: 0014-net-mvpp2-allocate-zeroed-tx-descriptors.patch
Patch8015: 0015-net-mvpp2-fix-the-RSS-table-entry-offset.patch
Patch8016: 0016-net-mvpp2-only-free-the-TSO-header-buffers-when-it-w.patch
Patch8017: 0017-net-mvpp2-split-the-max-ring-size-from-the-default-o.patch
Patch8018: 0018-net-mvpp2-align-values-in-ethtool-get_coalesce.patch
Patch8019: 0019-net-mvpp2-report-the-tx-usec-coalescing-information-.patch
Patch8020: 0020-net-mvpp2-adjust-the-coalescing-parameters.patch
Patch8021: 0021-device-property-Introduce-fwnode_get_mac_address.patch
Patch8022: 0022-device-property-Introduce-fwnode_get_phy_mode.patch
Patch8023: 0023-device-property-Introduce-fwnode_irq_get.patch
Patch8024: 0024-device-property-Allow-iterating-over-available-child.patch
Patch8025: 0025-net-mvpp2-simplify-maintaining-enabled-ports-list.patch
Patch8026: 0026-net-mvpp2-use-device_-fwnode_-APIs-instead-of-of_.patch
Patch8027: 0027-net-mvpp2-enable-ACPI-support-in-the-driver.patch
Patch8028: 0028-mvpp2-fix-multicast-address-filter.patch
Patch8029: 0029-net-mvpp2-Add-hardware-offloading-for-VLAN-filtering.patch
Patch8030: 0030-net-mvpp2-use-the-same-buffer-pool-for-all-ports.patch
Patch8031: 0031-net-mvpp2-update-the-BM-buffer-free-destroy-logic.patch
Patch8032: 0032-net-mvpp2-use-a-data-size-of-10kB-for-Tx-FIFO-on-por.patch
Patch8033: 0033-net-mvpp2-enable-UDP-TCP-checksum-over-IPv6.patch
Patch8034: 0034-net-mvpp2-jumbo-frames-support.patch
Patch8035: 0035-net-mvpp2-mvpp2_check_hw_buf_num-can-be-static.patch
Patch8036: 0036-net-mvpp2-Simplify-MAC-filtering-function-parameters.patch
Patch8037: 0037-net-mvpp2-Add-support-for-unicast-filtering.patch
Patch8038: 0038-net-mvpp2-use-correct-index-on-array-mvpp2_pools.patch
Patch8039: 0039-net-mvpp2-Make-mvpp2_prs_hw_read-a-parser-entry-init.patch
Patch8040: 0040-net-mvpp2-Don-t-use-dynamic-allocs-for-local-variabl.patch
Patch8041: 0041-net-mvpp2-Use-relaxed-I-O-in-data-path.patch
Patch8042: 0042-net-mvpp2-Fix-parser-entry-init-boundary-check.patch
Patch8043: 0043-net-mvpp2-Fix-TCAM-filter-reserved-range.patch
Patch8044: 0044-net-mvpp2-Fix-DMA-address-mask-size.patch
Patch8045: 0045-net-mvpp2-Fix-clk-error-path-in-mvpp2_probe.patch
Patch8046: 0046-net-mvpp2-Fix-clock-resource-by-adding-missing-mg_co.patch
#Ampere patches
Patch9001: 0001-BACKPORT-arm64-cmpwait-Clear-event-register-before-a.patch
Patch9002: 0002-BACKPORT-arm64-barrier-Implement-smp_cond_load_relax.patch
Patch9003: 0003-BACKPORT-arm64-locking-Replace-ticket-lock-implement.patch
Patch9004: 0004-BACKPORT-arm64-kconfig-Ensure-spinlock-fastpaths-are.patch
Patch9005: 0005-BACKPORT-ahci-Disable-LPM-on-Lenovo-50-series-laptop.patch
Patch9006: 0006-BACKPORT-ACPI-bus-Introduce-acpi_get_match_data-func.patch
Patch9007: 0007-BACKPORT-ACPI-bus-Remove-checks-in-acpi_get_match_da.patch
Patch9008: 0008-BACKPORT-ACPI-bus-Rename-acpi_get_match_data-to-acpi.patch
Patch9009: 0009-BACKPORT-ata-Disable-AHCI-ALPM-feature-for-Ampere-Co.patch
Patch9010: 0010-BACKPORT-perf-xgene-Fix-IOB-SLOW-PMU-parser-error.patch
Patch9011: 0011-BACKPORT-iommu-enable-bypass-transaction-caching-for.patch
#Pvsched patches
Patch9051: 0001-arm-paravirt-Use-a-single-ops-structure.patch
Patch9052: 0002-KVM-arm-arm64-Factor-out-hypercall-handling-from-PSC.patch
Patch9053: 0003-KVM-Implement-kvm_put_guest.patch
Patch9054: 0004-arm-arm64-Provide-a-wrapper-for-SMCCC-1.1-calls.patch
Patch9055: 0005-locking-osq-Use-optimized-spinning-loop-for-arm64.patch
Patch9056: 0006-arm64-spinlock-fix-a-Wunused-function-warning.patch
Patch9057: 0007-KVM-Boost-vCPUs-that-are-delivering-interrupts.patch
Patch9058: 0008-KVM-Check-preempted_in_kernel-for-involuntary-preemp.patch
Patch9059: 0009-KVM-arm64-Document-PV-sched-interface.patch
Patch9060: 0010-KVM-arm64-Implement-PV_SCHED_FEATURES-call.patch
Patch9061: 0011-KVM-arm64-Support-pvsched-preempted-via-shared-struc.patch
Patch9062: 0012-KVM-arm64-Add-interface-to-support-vCPU-preempted-ch.patch
Patch9063: 0013-KVM-arm64-Support-the-vCPU-preemption-check.patch
Patch9064: 0014-KVM-arm64-Add-SMCCC-PV-sched-to-kick-cpu.patch
Patch9065: 0015-KVM-arm64-Implement-PV_SCHED_KICK_CPU-call.patch
Patch9066: 0016-qspinlock-CNA-Add-ARM64-support.patch
Patch9067: 0017-locking-pvqspinlock-Extend-node-size-when-pvqspinloc.patch
Patch9068: 0018-locking-qspinlock-Introduce-CNA-into-the-slow-path-o.patch
Patch9069: 0019-locking-qspinlock-Introduce-starvation-avoidance-int.patch
Patch9070: 0020-locking-qspinlock-Introduce-the-shuffle-reduction-op.patch
Patch9071: 0021-KVM-arm64-Add-interface-to-support-PV-qspinlock.patch
Patch9072: 0022-locking-qspinlock-Merge-struct-__qspinlock-into-stru.patch
Patch9073: 0023-locking-qspinlock-Fix-build-for-anonymous-union-in-o.patch
Patch9074: 0024-KVM-arm64-Enable-PV-qspinlock.patch
Patch9075: 0025-KVM-arm64-Add-tracepoints-for-PV-qspinlock.patch


BuildRoot: %{_tmppath}/%{src_pkg_name}-%{KVRA}-root

%description
The %{src_pkg_name} package contains the Linux kernel sources. The Linux kernel
is the core of any Linux operating system.  The kernel handles the basic
functions of the operating system: memory allocation, process allocation, device
input and output, etc.


%package -n %{bin_pkg_name}
Summary: The Linux kernel
Group: System Environment/Kernel
%kernel_reqprovconf

%description -n %{bin_pkg_name}
The %{bin_pkg_name} package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions of the operating
system: memory allocation, process allocation, device input and output, etc.


%package -n %{bin_pkg_name}-doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
AutoReqProv: no
%description -n %{bin_pkg_name}-doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package -n %{bin_pkg_name}-headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description -n %{bin_pkg_name}-headers
%{bin_pkg_name}-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package -n %{bin_pkg_name}-bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description -n %{bin_pkg_name}-bootwrapper
%{bin_pkg_name}-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{bin_pkg_name}-debuginfo packages
Group: Development/Debug
%description -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
This package is required by %{bin_pkg_name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf%{?bin_suffix:-%{bin_suffix}}
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf%{?bin_suffix:-%{bin_suffix}}
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}

%package -n python-perf%{?bin_suffix:-%{bin_suffix}}
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf%{?bin_suffix:-%{bin_suffix}}
The python-perf%{?bin_suffix:-%{bin_suffix}} package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}

%package -n %{bin_pkg_name}-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:2.0
Requires: %{bin_pkg_name}-tools-libs = %{version}-%{release}
%description -n %{bin_pkg_name}-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n %{bin_pkg_name}-tools-libs
Summary: Libraries for the %{bin_pkg_name}-tools
Group: Development/System
License: GPLv2
%description -n %{bin_pkg_name}-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n %{bin_pkg_name}-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: %{bin_pkg_name}-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: %{bin_pkg_name}-tools-libs = %{version}-%{release}
%description -n %{bin_pkg_name}-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n %{bin_pkg_name}-tools-debuginfo
Summary: Debug information for package %{bin_pkg_name}-tools
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n %{bin_pkg_name}-tools-debuginfo
This package provides debug information for package %{bin_pkg_name}-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|XXX' -o tools-debuginfo.list}

%endif # with_tools

%if %{with_gcov}
%package -n %{bin_pkg_name}-gcov
Summary: gcov graph and source files for coverage data collection.
Group: Development/System
%description -n %{bin_pkg_name}-gcov
kernel-gcov includes the gcov graph and source files for gcov coverage collection.
%endif

%package -n %{bin_pkg_name}-abi-whitelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol whitelists
Group: System Environment/Kernel
AutoReqProv: no
%description -n %{bin_pkg_name}-abi-whitelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package -n %{bin_pkg_name}-%{?1:%{1}-}debuginfo\
Summary: Debug information for package %{bin_pkg_name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{bin_pkg_name}-%{?1:%{1}-}debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{bin_pkg_name}-%{?1:%{1}-}debuginfo\
This package provides debug information for package %{bin_pkg_name}%{?1:-%{1}}.\
This is required to use SystemTap with %{bin_pkg_name}%{?1:-%{1}}-%{KVRA}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVRA}%{?1:\.%{1}}/.*|/.*%%{KVRA}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package -n %{bin_pkg_name}-%{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: %{bin_pkg_name}-%{?1:%{1}-}devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVRA}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n %{bin_pkg_name}-%{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package -n %{bin_pkg_name}-%1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description -n %{bin_pkg_name}-debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description -n %{bin_pkg_name}-kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_default}
echo "Cannot build --with baseonly, default kernel build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

%setup -q -n %{src_pkg_name}-%{rheltarball} -c
mv linux-%{rheltarball} linux-%{KVRA}
cd linux-%{KVRA}

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/%{src_pkg_name}-%{version}-*.config .

ApplyOptionalPatch linux-kernel-test.patch

# Any further pre-build tree manipulations happen here.

if [ ! -d .git ]; then
  git init
  git config user.email "noreply@centos.org"
  git config user.name "AltArch Kernel"
  git config gc.auto 0
  git add .
  git commit -a -q -m "baseline"
fi

#Altarch patches
git am %{PATCH8001}
git am %{PATCH8002}
git am %{PATCH8003}
git am %{PATCH8004}
git am %{PATCH8005}
git am %{PATCH8006}
git am %{PATCH8007}
git am %{PATCH8008}
git am %{PATCH8009}
git am %{PATCH8010}
git am %{PATCH8011}
git am %{PATCH8012}
git am %{PATCH8013}
git am %{PATCH8014}
git am %{PATCH8015}
git am %{PATCH8016}
git am %{PATCH8017}
git am %{PATCH8018}
git am %{PATCH8019}
git am %{PATCH8020}
git am %{PATCH8021}
git am %{PATCH8022}
git am %{PATCH8023}
git am %{PATCH8024}
git am %{PATCH8025}
git am %{PATCH8026}
git am %{PATCH8027}
git am %{PATCH8028}
git am %{PATCH8029}
git am %{PATCH8030}
git am %{PATCH8031}
git am %{PATCH8032}
git am %{PATCH8033}
git am %{PATCH8034}
git am %{PATCH8035}
git am %{PATCH8036}
git am %{PATCH8037}
git am %{PATCH8038}
git am %{PATCH8039}
git am %{PATCH8040}
git am %{PATCH8041}
git am %{PATCH8042}
git am %{PATCH8043}
git am %{PATCH8044}
git am %{PATCH8045}
git am %{PATCH8046}

git am %{PATCH9001}
git am %{PATCH9002}
git am %{PATCH9003}
git am %{PATCH9004}
git am %{PATCH9005}
git am %{PATCH9006}
git am %{PATCH9007}
git am %{PATCH9008}
git am %{PATCH9009}
git am %{PATCH9010}
git am %{PATCH9011}

git am %{PATCH9051}
git am %{PATCH9052}
git am %{PATCH9053}
git am %{PATCH9054}
git am %{PATCH9055}
git am %{PATCH9056}
git am %{PATCH9057}
git am %{PATCH9058}
git am %{PATCH9059}
git am %{PATCH9060}
git am %{PATCH9061}
git am %{PATCH9062}
git am %{PATCH9063}
git am %{PATCH9064}
git am %{PATCH9065}
git am %{PATCH9066}
git am %{PATCH9067}
git am %{PATCH9068}
git am %{PATCH9069}
git am %{PATCH9070}
git am %{PATCH9071}
git am %{PATCH9072}
git am %{PATCH9073}
git am %{PATCH9074}
git am %{PATCH9075}

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
	mkdir configs
fi

# Remove configs not for the buildarch
for cfg in %{src_pkg_name}-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f %{src_pkg_name}-%{version}-*debug.config
%endif

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
%endif

# Setup CONFIG_SYSTEM_TRUSTED_KEYS="certs/rhel.pem" for module signing. And make
# sure we create the file with certificates and copy key generation configuration
for i in *.config
do
  sed -i 's@CONFIG_SYSTEM_TRUSTED_KEYS=.*@CONFIG_SYSTEM_TRUSTED_KEYS="certs/centos.pem"@' $i
done
cp %{SOURCE11} ./certs # x509.genkey
openssl x509 -inform der -in %{_sourcedir}/centos-ldup.x509 -out centos-ldup.pem
openssl x509 -inform der -in %{_sourcedir}/centos-kpatch.x509 -out centos-kpatch.pem
cat centos-ldup.pem centos-kpatch.pem > ./certs/centos.pem

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make %{?cross_opts} ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make %{?cross_opts} ARCH=$Arch oldnoconfig
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK='sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug -i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=%{src_pkg_name}-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVRA}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{KVRA}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # and now to start the build process

    make %{?cross_opts} -s mrproper

    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

%ifarch s390x
    if [ "$Flavour" == "kdump" ]; then
        pushd arch/s390/boot
        gcc -static -o zfcpdump zfcpdump.c
        popd
    fi
%endif

    make -s %{?cross_opts} ARCH=$Arch oldnoconfig >/dev/null
    make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" $MakeTarget %{?sparse_mflags}

    if [ "$Flavour" != "kdump" ]; then
        make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" modules %{?sparse_mflags} || exit 1
    fi

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
# EFI SecureBoot signing, x86_64-only
%ifarch x86_64
    %pesign -s -i $KernelImage -o $KernelImage.signed -a %{SOURCE13} -c %{SOURCE14} -n %{pesign_name}
    mv $KernelImage.signed $KernelImage
%endif
    $CopyKernel $KernelImage $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/kernel
    if [ "$Flavour" != "kdump" ]; then
        # Override $(mod-fw) because we don't want it to install any firmware
        # we'll get it from the linux-firmware package and we don't want conflicts
        make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
%if %{with_gcov}
	# install gcov-needed files to $BUILDROOT/$BUILD/...:
	#   gcov_info->filename is absolute path
	#   gcno references to sources can use absolute paths (e.g. in out-of-tree builds)
	#   sysfs symlink targets (set up at compile time) use absolute paths to BUILD dir
	find . \( -name '*.gcno' -o -name '*.[chS]' \) -exec install -D '{}' "$RPM_BUILD_ROOT/$(pwd)/{}" \;
%endif
    fi
%ifarch %{vdso_arches}
    make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{bin_pkg_name}-$KernelVer.conf
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc64 ppc64le
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/$Arch/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    if [ -d arch/$Arch/tools ]; then
      cp -a arch/$Arch/tools $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch || :
    fi
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # some arch/arm64 header files refer to arch/arm, so include them too
    cp -a --parents arch/arm/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # include/trace/events/wbt.h uses blk-{wbt,stat}.h private kernel headers,
    # and systemtap uses wbt.h when we run a script which uses wbt:* trace points
    cp block/blk-{wbt,stat}.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/block/

    # copy objtool for kernel-devel (needed for building external modules)
    if grep -q CONFIG_STACK_VALIDATION=y .config; then
      mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool
    fi

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
    collect_modules_list block 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm 'drm_open|drm_init'
    collect_modules_list modesetting 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    rm -f modinfo modnames

    # Save off the .tmp_versions/ directory.  We'll use it in the
    # __debug_install_post macro below to sign the right things
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp certs/signing_key.pem signing_key.pem.sign${Flavour:+.${Flavour}}
    cp certs/signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap softdep devname
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVRA}

%if %{with_default}
BuildKernel %make_target %kernel_image
%endif

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_kdump}
BuildKernel %make_target %kernel_image kdump
%endif

%global perf_make make %{?_smp_mflags} -C tools/perf -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 prefix=%{_prefix} lib=%{_lib}
%if %{with_perf}
# perf
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?cross_opts} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   make
   popd
   pushd tools/power/x86/turbostat
   make
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools
make tmon
popd
%endif

%if %{with_doc}
# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke 'make modules_sign' and the mod-extra-sign.sh
# commands to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Finally, pick a module at random and check that it's signed and fail the build
# if it isn't.

%define __modsign_install_post \
  if [ "%{with_debug}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign.debug .tmp_versions \
    mv signing_key.pem.sign.debug signing_key.pem \
    mv signing_key.x509.sign.debug signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA}.debug || exit 1 \
  fi \
    if [ "%{with_default}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-%{_target_cpu}.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign .tmp_versions \
    mv signing_key.pem.sign signing_key.pem \
    mv signing_key.x509.sign signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA} || exit 1 \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs xz; \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif

%endif

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVRA}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}

# copy the source over
mkdir -p $docdir
tar -f - --exclude='.*' -c Documentation | tar xf - -C $docdir

%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \( -name .install -o -name .check -o -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE25} -C $INSTALL_KABI_PATH
%endif  # with_kernel_abi_whitelists

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install
# remove the 'trace' symlink.
rm -f $RPM_BUILD_ROOT/%{_bindir}/trace

# perf-python extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT try-install-man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
make INSTALL_ROOT=%{buildroot} install
popd
%endif

%endif

%if %{with_bootwrapper}
make %{?cross_opts} ARCH=%{hdrarch} DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif

%if %{with_doc}
# Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}
install -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}/kernel-signing-ca.cer
%endif

###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n %{bin_pkg_name}-tools
/sbin/ldconfig

%postun -n %{bin_pkg_name}-tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post -n %{bin_pkg_name}-%{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVRA}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f\
     done)\
fi\
%{nil}


# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans -n %{bin_pkg_name}%{?1:-%{1}}}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVRA}%{?-v:.%{-v*}} || exit $?\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?1:-%{1}} --rpmposttrans %{KVRA}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post -n %{bin_pkg_name}%{?-v:-%{-v*}}}\
%{-r:\
if [ `uname -i` == "x86_64" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?-v:-%{-v*}} --install %{KVRA}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun -n %{bin_pkg_name}%{?1:-%{1}}}\
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVRA}%{?1:.%{1}} || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post 

%kernel_variant_preun debug
%kernel_variant_post -v debug

%ifarch s390x
%postun -n %{bin_pkg_name}-kdump
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVRA}.kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*.kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi

%post -n %{bin_pkg_name}-kdump
    ln -sf /boot/vmlinuz-%{KVRA}.kdump /boot/zfcpdump
%endif # s390x

###
### file lists
###

%if %{with_headers}
%files -n %{bin_pkg_name}-headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files -n %{bin_pkg_name}-bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files -n %{bin_pkg_name}-doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}/kernel-signing-ca.cer
%dir %{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}
%dir %{_datadir}/doc/kernel-keys
%endif

%if %{with_kernel_abi_whitelists}
%files -n %{bin_pkg_name}-abi-whitelists
%defattr(-,root,root,-)
/lib/modules/kabi-*
%endif

%if %{with_perf}
%files -n perf%{?bin_suffix:-%{bin_suffix}}
%defattr(-,root,root)
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_libdir}/traceevent
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%{_datadir}/perf-core/strace/groups
%{_datadir}/doc/perf-tip/tips.txt

%files -n python-perf%{?bin_suffix:-%{bin_suffix}}
%defattr(-,root,root)
%{python_sitearch}

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
%defattr(-,root,root)

%files -f python-perf-debuginfo.list -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
%defattr(-,root,root)
%endif
%endif

%if %{with_tools}
%files -n %{bin_pkg_name}-tools -f cpupower.lang
%defattr(-,root,root)
%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%endif
%{_bindir}/tmon
%if %{with_debuginfo}
%files -f tools-debuginfo.list -n %{bin_pkg_name}-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n %{bin_pkg_name}-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n %{bin_pkg_name}-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif

%endif # with_tools

%if %{with_gcov}
%ifarch x86_64 s390x ppc64 ppc64le
%files -n %{bin_pkg_name}-gcov
%defattr(-,root,root)
%{_builddir}
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files -n %{bin_pkg_name}%{?2:-%{2}}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVRA}%{?2:.%{2}}\
/%{image_install_path}/.vmlinuz-%{KVRA}%{?2:.%{2}}.hmac \
%attr(600,root,root) /boot/System.map-%{KVRA}%{?2:.%{2}}\
/boot/symvers-%{KVRA}%{?2:.%{2}}.gz\
/boot/config-%{KVRA}%{?2:.%{2}}\
%dir /lib/modules/%{KVRA}%{?2:.%{2}}\
/lib/modules/%{KVRA}%{?2:.%{2}}/kernel\
/lib/modules/%{KVRA}%{?2:.%{2}}/build\
/lib/modules/%{KVRA}%{?2:.%{2}}/source\
/lib/modules/%{KVRA}%{?2:.%{2}}/extra\
/lib/modules/%{KVRA}%{?2:.%{2}}/updates\
/lib/modules/%{KVRA}%{?2:.%{2}}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVRA}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/%{bin_pkg_name}-%{KVRA}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVRA}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVRA}%{?2:.%{2}}.img\
%{expand:%%files -n %{bin_pkg_name}-%{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVRA}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list -n %{bin_pkg_name}-%{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_default}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_kdump} kdump

%changelog
* Wed Sep 23 2020 gaozhekang <864647692@qq.com>
- Add pvsched feature to support vcpu preempt and pvqspinlock

* Tue Nov 13 2018 Johnny Hughes <johnny@centos.org> [4.14.0-49.13.1.el7a]
- Rolled in CentOS certificates and signed modules with a CentOS certificate.
- Turned off CONFIG_CPU_FREQ_DEFAULT_GOV_ONDEMAND and turned on CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE on aarch64
- added git as buildrequirement to do patches (if/when required)
- added 46 MVPP2 patches
- set CONFIG_ARCH_MVEBU=y, CONFIG_MVPP2=m, CONFIG_MARVELL_10G_PHY=m on aarch64

* Tue Sep 25 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-115.el7a]
- [fs] fanotify: fix fsnotify_prepare_user_wait() failure (Miklos Szeredi) [1631194]
- [fs] fsnotify: fix pinning group in fsnotify_prepare_user_wait() (Miklos Szeredi) [1631194]
- [fs] fsnotify: pin both inode and vfsmount mark (Miklos Szeredi) [1631194]
- [fs] fsnotify: clean up fsnotify_prepare/finish_user_wait() (Miklos Szeredi) [1631194]

* Mon Sep 24 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-114.el7a]
- [block] blkdev: __blkdev_direct_io_simple: fix leak in error case (Ming Lei) [1602223]
- [block] bio_iov_iter_get_pages: pin more pages for multi-segment IOs (Ming Lei) [1602223]
- [block] bio_iov_iter_get_pages: fix size of last iovec (Ming Lei) [1602223]
- [net] udp4: fix IP_CMSG_CHECKSUM for connected sockets (Andrea Claudi) [1625958]
- [net] udp6: add missing checks on edumux packet processing (Andrea Claudi) [1625958]
- [fs] ext4: fix false negatives *and* false positives in ext4_check_descriptors() (Lukas Czerner) [1607353] {CVE-2018-10878}
- [fs] ext4: make sure bitmaps and the inode table don't overlap with bg descriptors (Lukas Czerner) [1607353] {CVE-2018-10878}
- [fs] ext4: always check block group bounds in ext4_init_block_bitmap() (Lukas Czerner) [1607353] {CVE-2018-10878}
- [cdrom] information leak in cdrom_ioctl_media_changed() (Sanskriti Sharma) [1578209] {CVE-2018-10940}
- [fs] nfs: lockd: fix "list_add double add" caused by legacy signal interface ("J. Bruce Fields") [1600442]
- [nvme] pci: move nvme_kill_queues to nvme_remove_dead_ctrl (Ming Lei) [1612743]

* Tue Sep 18 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-113.el7a]
- [net] ip: frags: fix crash in ip_do_fragment() (Sabrina Dubroca) [1629658] {CVE-2018-14641}
- [kernel] posix-timer: Properly check sigevent->sigev_notify (Phil Auld) [1613718] {CVE-2017-18344}
- [fs] ext4: update i_disksize if direct write past ondisk size (Lukas Czerner) [1554214]
- [fs] ext4: protect i_disksize update by i_data_sem in direct write path (Lukas Czerner) [1554214]
- [fs] ext4: update mtime in ext4_punch_hole even if no blocks are released (Lukas Czerner) [1554214]
- [fs] ext4: fix interaction between i_size, fallocate, and delalloc after a crash (Lukas Czerner) [1554214]
- [fs] ext4: set h_journal if there is a failure starting a reserved handle (Lukas Czerner) [1554214]
- [fs] ext4: verify the depth of extent tree in ext4_find_extent() (Lukas Czerner) [1602821] {CVE-2018-10877}
- [fs] ext4: never move the system.data xattr out of the inode body (Lukas Czerner) [1605633] {CVE-2018-10880}
- [fs] ext4: clear i_data in ext4_inode_info when removing inline data (Lukas Czerner) [1607600] {CVE-2018-10881}
- [fs] ext4: add more inode number paranoia checks (Lukas Czerner) [1609237] {CVE-2018-10882}
- [fsnotify] Fix fsnotify_mark_connector race (Miklos Szeredi) [1596532]
- [fs] Fix up non-directory creation in SGID directories (Miklos Szeredi) [1600958] {CVE-2018-13405}
- [mm] madvise: fix madvise() infinite loop under special circumstances (Rafael Aquini) [1552983] {CVE-2017-18208}
- [mm] oom: fix concurrent munlock and oom reaper unmap (Rafael Aquini) [1570542] {CVE-2018-1000200}
- [fs] cifs: Fix slab-out-of-bounds in send_set_info() on SMB2 ACE setting (Leif Sahlberg) [1598772]
- [scsi] core: run queue if SCSI device queue isn't ready and queue is idle (Ming Lei) [1627969]
- [iommu] arm-smmu: workaround DMA mode issues (Mark Salter) [1596055]
- [powerpc] tm: Fix HFSCR bit for no suspend case (Gustavo Duarte) [1628637]
- [powerpc] vdso: Correct call frame information (Desnes Augusto Nunes do Rosario) [1627647]
- [fs] ext4: limit xattr size to INT_MAX (Lukas Czerner) [1564531] {CVE-2018-1095}
- [fs] ext4: fail ext4_iget for root directory if unallocated (Lukas Czerner) [1564592] {CVE-2018-1092}
- [fs] ext4: don't allow r/w mounts if metadata blocks overlap the superblock (Lukas Czerner) [1564563] {CVE-2018-1094}
- [fs] ext4: add MODULE_SOFTDEP to ensure crc32c is included in the initramfs (Lukas Czerner) [1564563] {CVE-2018-1094}
- [fs] ext4: always initialize the crc32c checksum driver (Lukas Czerner) [1564563] {CVE-2018-1094}
- [fs] ext4: always verify the magic number in xattr blocks (Lukas Czerner) [1607578] {CVE-2018-10879}
- [fs] ext4: move call to ext4_error() into ext4_xattr_check_block() (Lukas Czerner) [1607578] {CVE-2018-10879}
- [fs] ext4: add corruption check in ext4_xattr_set_entry() (Lukas Czerner) [1607578] {CVE-2018-10879}
- [fs] jbd2: don't mark block as modified if the handle is out of credits (Lukas Czerner) [1609762] {CVE-2018-10883}
- [fs] ext4: avoid running out of journal credits when appending to an inline file (Lukas Czerner) [1609762] {CVE-2018-10883}
- [irqchip] gic-v3-its: Cap lpi_id_bits to reduce memory footprint (Mark Salter) [1625315]
- [irqchip] gic-v3-its: Reduce minimum LPI allocation to 1 for PCI devices (Mark Salter) [1625315]
- [irqchip] gic-v3-its: Honor hypervisor enforced LPI range (Mark Salter) [1625315]
- [irqchip] gic-v3: Expose GICD_TYPER in the rdist structure (Mark Salter) [1625315]
- [irqchip] gic-v3-its: Drop chunk allocation compatibility (Mark Salter) [1625315]
- [irqchip] gic-v3-its: Move minimum LPI requirements to individual busses (Mark Salter) [1625315]
- [irqchip] gic-v3-its: Use full range of LPIs (Mark Salter) [1625315]
- [irqchip] gic-v3-its: Refactor LPI allocator (Mark Salter) [1625315]

* Fri Sep 14 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-112.el7a]
- [vhost] fix info leak due to uninitialized memory (Jason Wang) [1573706] {CVE-2018-1118}
- [powerpc] kprobes: Fix call trace due to incorrect preempt count (Jiri Olsa) [1610512]
- [fs] dcache: Avoid livelock between d_alloc_parallel and __d_add (Robert Richter) [1613285]
- [arm64] kvm: Move VCPU_WORKAROUND_2_FLAG macros to the top of the file (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Add ARCH_WORKAROUND_2 discovery through ARCH_FEATURES_FUNC_ID (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Handle guest's ARCH_WORKAROUND_2 requests (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Add ARCH_WORKAROUND_2 support for guests (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Add HYP per-cpu accessors (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] ssbd: Add prctl interface for per-thread mitigation (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] ssbd: Introduce thread flag to control userspace mitigation (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] ssbd: Restore mitigation status on CPU resume (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] ssbd: Skip apply_ssbd if not using dynamic mitigation (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] ssbd: Add global mitigation state accessor (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] Add 'ssbd' command-line option (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] Add ARCH_WORKAROUND_2 probing (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] Add per-cpu infrastructure to call ARCH_WORKAROUND_2 (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] Call ARCH_WORKAROUND_2 on transitions between EL0 and EL1 (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] smccc: Add SMCCC-specific return codes (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Avoid storing the vcpu pointer on the stack (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Stop save/restoring host tpidr_el1 on VHE (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] alternatives: use tpidr_el2 on VHE hosts (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Change hyp_panic()s dependency on tpidr_el2 (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] Convert kvm_host_cpu_state to a static per-cpu allocation (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] kvm: Store vcpu on the stack during __guest_enter() (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] prctl: Add force disable speculation (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] nospec: Allow getting/setting on non-current task (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] seccomp: Enable speculation flaw mitigations (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] proc: Provide details on speculation flaw mitigations (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] prctl: Add speculation control prctls (Jeremy Linton) [1596417] {CVE-2018-3639}
- [arm64] fixup: vfs, fdtable: Prevent bounds-check bypass via speculative execution (Jeremy Linton) [1596417] {CVE-2018-3639}

* Thu Sep 13 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-111.el7a]
- [powerpc] kvm: book3s hv: Don't truncate HPTE index in xlate function (David Gibson) [1613839]
- [char] ipmi: Fix I2C client removal in the SSIF driver (Robert Richter) [1624907]
- [char] ipmi: Rework SMI registration failure (Robert Richter) [1624907]
- [char] ipmi: Cleanup oops on initialization failure (Robert Richter) [1624907]
- [char] ipmi_ssif: Fix uninitialized variable issue (Robert Richter) [1624907]
- [char] ipmi_si: Clean up shutdown a bit (Robert Richter) [1624907]
- [char] ipmi: ipmi_unregister_smi() cannot fail, have it return void (Robert Richter) [1624907]
- [char] ipmi_si: Convert over to a shutdown handler (Robert Richter) [1624907]
- [char] ipmi: Rework locking and shutdown for hot remove (Robert Richter) [1624907]
- [char] ipmi: Fix some counter issues (Robert Richter) [1624907]
- [char] ipmi: Change ipmi_smi_t to struct ipmi_smi * (Robert Richter) [1624907]
- [char] ipmi: Rename ipmi_user_t to struct ipmi_user * (Robert Richter) [1624907]
- [char] ipmi: Consolidate cleanup code (Robert Richter) [1624907]
- [char] ipmi: Fix some error cleanup issues (Robert Richter) [1624907]
- [powerpc] kvm: book3s hv: Don't use compound_order to determine host mapping size (David Gibson) [1609129]
- [powerpc] kvm: book3s hv: radix: Refine IO region partition scope attributes (David Gibson) [1609129]
- [powerpc] kvm: book3s hv: Use __gfn_to_pfn_memslot() in page fault handler (David Gibson) [1609129]
- [powerpc] kvm: book3s hv: Handle 1GB pages in radix page fault handler (David Gibson) [1609129]
- [powerpc] kvm: book3s hv: Radix page fault handler optimizations (David Gibson) [1609129]
- [powerpc] kvm: book3s hv: Streamline setting of reference and change bits (David Gibson) [1609129]
- [powerpc] kvm: ppc: Avoid marking DMA-mapped pages dirty in real mode (David Gibson) [1620360]
- [powerpc] powernv/ioda: Allocate indirect TCE levels on demand (David Gibson) [1620360]
- [powerpc] powernv: Rework TCE level allocation (David Gibson) [1620360]
- [powerpc] powernv: Add indirect levels to it_userspace (David Gibson) [1620360]
- [powerpc] kvm: ppc: Make iommu_table::it_userspace big endian (David Gibson) [1620360]
- [powerpc] kvm: ppc: book3s: Allow backing bigger guest IOMMU pages with smaller physical pages (David Gibson) [1620360]
- [powerpc] powernv: Move TCE manupulation code to its own file (David Gibson) [1620360]
- [powerpc] ioda: Use ibm, supported-tce-sizes for IOMMU page size mask (David Gibson) [1620360]
- [powerpc] powernv/ioda: Remove explicit max window size check (David Gibson) [1620360]
- [s390] lib: use expoline for all bcr instructions (Hendrik Brueckner) [1625206]
- [s390] kvm: force bp isolation for VSIE (Hendrik Brueckner) [1625206]

* Mon Sep 10 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-110.el7a]
- [net] ip: process in-order fragments efficiently (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] ipv6: defrag: drop non-last frags smaller than min mtu (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] modify skb_rbtree_purge to return the truesize of all purged skbs (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] ipv4: frags: precedence bug in ip_expire() (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] ip: use rb trees for IP frag queue (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] inet: frags: do not clone skb in ip_expire() (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] inet: frags: get rif of inet_frag_evicting() (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] ip: discard IPv4 datagrams with overlapping segments (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] ipv4: frags: handle possible skb truesize change (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] inet: frags: get rid of ipfrag_skb_cb/FRAG_CB (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [net] speed up skb_rbtree_purge() (Sabrina Dubroca) [1613929] {CVE-2018-5391}
- [powerpc] kvm: book3s hv: Use correct pagesize in kvm_unmap_radix() (David Gibson) [1609115]
- [netdrv] cxgb4: update 1.20.8.0 as the latest firmware supported (Arjun Vynipadath) [1622553]
- [netdrv] cxgb4: update latest firmware version supported (Arjun Vynipadath) [1622553]
- [arm64] entry: Apply BP hardening for high-priority synchronous exceptions (Robert Richter) [1614914] {CVE-2017-5715 CVE-2017-5753 CVE-2017-5754}
- [powerpc] kvm: book3s: Fix guest DMA when guest partially backed by THP pages (David Gibson) [1613190]
- [powerpc] kvm: Check if IOMMU page is contained in the pinned physical page (David Gibson) [1613190]
- [vfio] spapr: Use IOMMU pageshift rather than pagesize (David Gibson) [1613190]
- [scsi] target: iscsi: cxgbit: fix max iso npdu calculation (Arjun Vynipadath) [1613308]
- [scsi] csiostor: update csio_get_flash_params() (Arjun Vynipadath) [1613308]
- [powerpc] mm/radix: Only need the Nest MMU workaround for R -> RW transition (Gustavo Duarte) [1625826]
- [powerpc] mm/books3s: Add new pte bit to mark pte temporarily invalid (Gustavo Duarte) [1625826]

* Tue Sep 04 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-109.el7a]
- [scsi] qla2xxx: Fix crash on qla2x00_mailbox_command (Himanshu Madhani) [1592456]
- [gpu] drm: udl: Properly check framebuffer mmap offsets (Ben Crocker) [1573097] {CVE-2018-8781}
- [scsi] libiscsi: fix possible NULL pointer dereference in case of TMF (Chris Leech) [1613266]
- [base] driver core: partially revert "driver core: correct device's shutdown order" (Pingfan Liu) [1507829]
- [scsi] lpfc: Fix list corruption on the completion queue (Dick Kennedy) [1615887]
- [scsi] lpfc: Fix driver crash when re-registering NVME rports (Dick Kennedy) [1615881]
- [scsi] lpfc: Correct LCB ACCept payload (Dick Kennedy) [1615879]
- [crypto] algif_aead: fix reference counting of null skcipher (Herbert Xu) [1600394]
- [netdrv] mlx5-core: Mark unsupported devices (Jonathan Toppins) [1623600 1623599]
- [media] v4l2-compat-ioctl32.c: make ctrl_is_pointer work for subdevs (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: refactor compat ioctl32 logic (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: don't copy back the result for certain errors (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: drop pr_info for unknown buffer type (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: copy clip list in put_v4l2_window32 (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: fix ctrl_is_pointer (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: copy m.userptr in put_v4l2_plane32 (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: avoid sizeof(type) (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: move 'helper' functions to __get/put_v4l2_format32 (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: fix the indentation (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-compat-ioctl32.c: add missing VIDIOC_PREPARE_BUF (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-ioctl.c: don't copy back the result for -ENOTTY (Jarod Wilson) [1548728] {CVE-2017-13166}
- [media] v4l2-ioctl.c: use check_fmt for enum/g/s/try_fmt (Jarod Wilson) [1548728] {CVE-2017-13166}

* Thu Aug 30 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-108.el7a]
- [net] sched: Fix missing res info when create new tc_index filter (Hangbin Liu) [1614741]
- [net] sched: fix NULL pointer dereference when delete tcindex filter (Hangbin Liu) [1614741]
- [redhat] configs: Enable CONFIG_IP_SET_HASH_IPMAC as module (Stefano Brivio) [1608662]
- [net] ipv6: send netlink notifications for manually configured addresses (Florian Westphal) [1605088]
- [netdrv] hns3: modify variable type in hns3_nic_reuse_page (Xiaojun Tan) [1622022]
- [netdrv] hns3: fix page_offset overflow when CONFIG_ARM64_64K_PAGES (Xiaojun Tan) [1622022]
- [netdrv] hns: use eth_get_headlen interface instead of hns_nic_get_headlen (Xiaojun Tan) [1622022]
- [netdrv] hns: fix skb->truesize underestimation (Xiaojun Tan) [1622022]
- [netdrv] hns: modify variable type in hns_nic_reuse_page (Xiaojun Tan) [1622022]
- [netdrv] hns: fix length and page_offset overflow when CONFIG_ARM64_64K_PAGES (Xiaojun Tan) [1622022]
- [netdrv] bnx2x: disable GSO where gso_size is too big for hardware (Jonathan Toppins) [1546762] {CVE-2018-1000026}
- [net] create skb_gso_validate_mac_len() (Jonathan Toppins) [1546762] {CVE-2018-1000026}
- [i2c] xlp9xx: Fix case where SSIF read transaction completes early (Robert Richter) [1610749]
- [i2c] xlp9xx: Make sure the transfer size is not more than I2C_SMBUS_BLOCK_SIZE (Robert Richter) [1610749]
- [i2c] xlp9xx: Fix issue seen when updating receive length (Robert Richter) [1610749]
- [i2c] xlp9xx: Add support for SMBAlert (Robert Richter) [1610749]
- [ipmi] ipmi_ssif: Remove usecount handling (Robert Richter) [1610749]
- [ipmi] ipmi_ssif: Convert over to a shutdown handler (Robert Richter) [1610749]
- [ipmi] Add shutdown functions for users and interfaces (Robert Richter) [1610749]
- [ipmi] Remove ACPI SPMI probing from the SSIF (I2C) driver (Robert Richter) [1610749]
- [infiniband] iw_cxgb4: correctly enforce the max reg_mr depth (Arjun Vynipadath) [1613318]
- [redhat] configs: enable CONFIG_VHOST_VSOCK and CONFIG_VIRTIO_VSOCKETS (David Gibson) [1619214]
- [acpi] sbshc: remove raw pointer from printk() message (Al Stone) [1547007] {CVE-2018-5750}

* Wed Aug 29 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-107.el7a]
- [tools] power: cpupower : Fix header name to read idle state name (Steve Best) [1619598]
- [arm64] kpti: Use early_param for kpti= command-line option (Xiaojun Tan) [1611957]
- [powerpc] eeh: avoid misleading message "eeh: no capable adapters found" (Steve Best) [1619377]
- [s390] uprobes: implement arch_uretprobe_is_alive() (Steve Best) [1615977]
- [powerpc] topology: Get topology for shared processors at boot (Steve Best) [1620038]
- [powerpc] fadump: cleanup crash memory ranges support (Steve Best) [1622084]
- [powerpc] fadump: merge adjacent memory ranges to reduce PT_LOAD segements (Steve Best) [1622084]
- [powerpc] fadump: handle crash memory ranges array index overflow (Steve Best) [1622084]
- [powerpc] fadump: Unregister fadump on kexec down path (Steve Best) [1622084]
- [powerpc] fadump: Do not use hugepages when fadump is active (Steve Best) [1622084]
- [powerpc] fadump: exclude memory holes while reserving memory in second kernel (Steve Best) [1622084]
- [powerpc] fadump: use kstrtoint to handle sysfs store (Steve Best) [1622084]
- [powerpc] powernv/pci: Work around races in PCI bridge enabling (Steve Best) [1619735]
- [powerpc] pci: Add wrappers for dev_printk() (Steve Best) [1619735]
- [s390] kvm: add etoken support for guests (Thomas Huth) [1622956]
- [s390] kvm: implement CPU model only facilities (Thomas Huth) [1622956]
- [s390] detect etoken facility (Thomas Huth) [1622956]

* Fri Aug 24 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-106.el7a]
- [netdrv] hns3: fix return value error while hclge_cmd_csq_clean failed (Xiaojun Tan) [1588892]
- [netdrv] hns3: Prevent sending command during global or core reset (Xiaojun Tan) [1588892]
- [netdrv] hns3: Optimize PF CMDQ interrupt switching process (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for VF mailbox receiving unknown message (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for VF mailbox cannot receiving PF response (Xiaojun Tan) [1588892]
- [netdrv] hns3: remove unused hclgevf_cfg_func_mta_filter (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix the process of adding broadcast addresses to tcam (Xiaojun Tan) [1588892]
- [netdrv] hns3: Optimize the VF's process of updating multicast MAC (Xiaojun Tan) [1588892]
- [netdrv] hns3: Optimize the PF's process of updating multicast MAC (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for vxlan tx checksum bug (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add missing break in misc_irq_handle (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for phy not link up problem after resetting (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for hclge_reset running repeatly problem (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for service_task not running problem after resetting (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix setting mac address error (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add repeat address checking for setting mac address (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add support for IFF_ALLMULTI flag (Xiaojun Tan) [1588892]
- [netdrv] hns3: Disable vf vlan filter when vf vlan table is full (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes initalization of RoCE handle and makes it conditional (Xiaojun Tan) [1588892]
- [netdrv] hns3: Adds support for led locate command for copper port (Xiaojun Tan) [1588892]
- [netdrv] hns3: Remove unused led control code (Xiaojun Tan) [1588892]
- [netdrv] hns3: Clear TX/RX rings when stopping port & un-initializing client (Xiaojun Tan) [1588892]
- [netdrv] hns3: Removes unnecessary check when clearing TX/RX rings (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes the init of the VALID BD info in the descriptor (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes the state to indicate client-type initialization (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for PF mailbox receving unknown message (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add support to enable TX/RX promisc mode for H/W rev(0x21) (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add STRP_TAGP field support for hardware revision 0x21 (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add support for tx_accept_tag2 and tx_accept_untag2 config (Xiaojun Tan) [1588892]
- [netdrv] hns3: Updates RX packet info fetch in case of multi BD (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for CMDQ and Misc. interrupt init order problem (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes kernel panic issue during rmmod hns3 driver (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for netdev not running problem after calling net_stop and net_open (Xiaojun Tan) [1588892]
- [netdrv] hns3: Use enums instead of magic number in hclge_is_special_opcode (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for hns3 module is loaded multiple times problem (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix the missing client list node initialization (Xiaojun Tan) [1588892]
- [netdrv] hns3: cleanup of return values in hclge_init_client_instance() (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes API to fetch ethernet header length with kernel default (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes error reported by Kbuild and internal review (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes the missing PCI iounmap for various legs (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add support of .sriov_configure in HNS3 driver (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for fiber link up problem (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes the back pressure setting when sriov is enabled (Xiaojun Tan) [1588892]
- [netdrv] hns3: Change return value in hnae3_register_client (Xiaojun Tan) [1588892]
- [netdrv] hns3: Change return type of hnae3_register_ae_algo (Xiaojun Tan) [1588892]
- [netdrv] hns3: Change return type of hnae3_register_ae_dev (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add a check for client instance init state (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for the null pointer problem occurring when initializing ae_dev failed (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for deadlock problem occurring when unregistering ae_algo (Xiaojun Tan) [1588892]
- [netdrv] hns3: refactor the loopback related function (Xiaojun Tan) [1588892]
- [netdrv] hns3: fix for cleaning ring problem (Xiaojun Tan) [1588892]
- [netdrv] hns3: remove add/del_tunnel_udp in hns3_enet module (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for setting mac address when resetting (Xiaojun Tan) [1588892]
- [netdrv] hns3: Add support of hardware rx-vlan-offload to HNS3 VF driver (Xiaojun Tan) [1588892]
- [netdrv] hns3: Remove packet statistics in the range of 8192~12287 (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix for packet loss due wrong filter config in VLAN tbls (Xiaojun Tan) [1588892]
- [netdrv] hns3: fix a dead loop in hclge_cmd_csq_clean (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fix to support autoneg only for port attached with phy (Xiaojun Tan) [1588892]
- [netdrv] hns3: fix for phy_addr error in hclge_mac_mdio_config (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes the error legs in hclge_init_ae_dev function (Xiaojun Tan) [1588892]
- [netdrv] hns3: Fixes the out of bounds access in hclge_map_tqp (Xiaojun Tan) [1588892]
- [netdrv] hns3: fix to correctly fetch l4 protocol outer header (Xiaojun Tan) [1588892]
- [netdrv] hns3: Remove error log when getting pfc stats fails (Xiaojun Tan) [1588892]
- [netdrv] hns3: Avoid action name truncation (Xiaojun Tan) [1588892]
- [netdrv] hns3: hns_dsaf_mac: Use generic eth_broadcast_addr (Xiaojun Tan) [1588892]

* Thu Aug 23 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-105.el7a]
- [infiniband] hns: Remove a set-but-not-used variable (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Update the implementation of set_mac (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Update the implementation of set_gid (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Add TPQ link table support (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Add TSQ link table support (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Fix endian conversions and annotations (Zhou Wang) [1600072]
- [infiniband] ib/hns: Use zeroing memory allocator instead of allocator/memset (Zhou Wang) [1600072]
- [infiniband] rdma/hns_roce: Don't check return value of zap_vma_ptes() (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Implement the disassociate_ucontext API (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Fix the illegal memory operation when cross page (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Add reset process for RoCE in hip08 (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Increase checking CMQ status timeout value (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Modify uar allocation algorithm to avoid bitmap exhaust (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Rename the idx field of db (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Move the location for initializing tmp_len (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Bugfix for cq record db for kernel (Zhou Wang) [1600072]
- [infiniband] rdma/hns: Drop local zgid in favor of core defined variable (Zhou Wang) [1600072]
- [netdrv] hinic: fix a problem in free_tx_poll() (Zhou Wang) [1614135]
- [netdrv] hinic: Link the logical network device to the pci device in sysfs (Zhou Wang) [1614135]
- [netdrv] hinic: fix a problem in hinic_xmit_frame() (Zhou Wang) [1614135]
- [netdrv] hinic: remove redundant pointer pfhwdev (Zhou Wang) [1614135]
- [netdrv] hinic: reset irq affinity before freeing irq (Zhou Wang) [1614135]
- [netdrv] ibmvnic: Update firmware error reporting with cause string (Steve Best) [1614661]
- [netdrv] ibmvnic: Remove code to request error information (Steve Best) [1614661]
- [netdrv] mlx5e: Properly check if hairpin is possible between two functions (Alaa Hleihel) [1611571]

* Mon Aug 13 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-104.el7a]
- [media] dvb_frontend: fix ifnullfree.cocci warnings (Jarod Wilson) [1546036] {CVE-2017-16648}
- [media] dvb_frontend: don't use-after-free the frontend struct (Jarod Wilson) [1546036] {CVE-2017-16648}
- [media] dvb-core: always call invoke_release() in fe_free() (Jarod Wilson) [1546036] {CVE-2017-16648}
- [net] tcp: add tcp_ooo_try_coalesce() helper (Marcelo Leitner) [1611382] {CVE-2018-5390}
- [net] tcp: call tcp_drop() from tcp_data_queue_ofo() (Marcelo Leitner) [1611382] {CVE-2018-5390}
- [net] tcp: detect malicious patterns in tcp_collapse_ofo_queue() (Marcelo Leitner) [1611382] {CVE-2018-5390}
- [net] tcp: avoid collapses in tcp_prune_queue() if possible (Marcelo Leitner) [1611382] {CVE-2018-5390}
- [net] tcp: free batches of packets in tcp_prune_ofo_queue() (Marcelo Leitner) [1611382] {CVE-2018-5390}
- [net] add rb_to_skb() and other rb tree helpers (Marcelo Leitner) [1611382] {CVE-2018-5390}

* Thu Aug 09 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-103.el7a]
- [scsi] hisi_sas: Update a couple of register settings for v3 hw (Zhou Wang) [1589697]
- [scsi] hisi_sas: Add missing PHY spinlock init (Zhou Wang) [1589697]
- [scsi] hisi_sas: Pre-allocate slot DMA buffers (Zhou Wang) [1589697]
- [scsi] hisi_sas: Release all remaining resources in clear nexus ha (Zhou Wang) [1589697]
- [scsi] hisi_sas: Add a flag to filter PHY events during reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: Adjust task reject period during host reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: Fix the conflict between dev gone and host reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: Only process broadcast change in phy_bcast_v3_hw() (Zhou Wang) [1589697]
- [scsi] hisi_sas: Use dmam_alloc_coherent() (Zhou Wang) [1589697]
- [scsi] hisi_sas: Mark PHY as in reset for nexus reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: Fix return value when get_free_slot() failed (Zhou Wang) [1589697]
- [scsi] hisi_sas: Terminate STP reject quickly for v2 hw (Zhou Wang) [1589697]
- [scsi] hisi_sas: Add v2 hw force PHY function for internal ATA command (Zhou Wang) [1589697]
- [scsi] hisi_sas: Include TMF elements in struct hisi_sas_slot (Zhou Wang) [1589697]
- [scsi] hisi_sas: Try wait commands before before controller reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: Init disks after controller reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: Create a scsi_host_template per HW module (Zhou Wang) [1589697]
- [scsi] hisi_sas: Reset disks when discovered (Zhou Wang) [1589697]
- [scsi] hisi_sas: Add LED feature for v3 hw (Zhou Wang) [1589697]
- [scsi] hisi_sas: Change common allocation mode of device id (Zhou Wang) [1589697]
- [scsi] hisi_sas: change slot index allocation mode (Zhou Wang) [1589697]
- [scsi] hisi_sas: Introduce hisi_sas_phy_set_linkrate() (Zhou Wang) [1589697]
- [scsi] hisi_sas: fix a typo in hisi_sas_task_prep() (Zhou Wang) [1589697]
- [scsi] hisi_sas: add check of device in hisi_sas_task_exec() (Zhou Wang) [1589697]
- [scsi] hisi_sas: Use device lock to protect slot alloc/free (Zhou Wang) [1589697]
- [scsi] hisi_sas: Don't lock DQ for complete task sending (Zhou Wang) [1589697]
- [scsi] hisi_sas: allocate slot buffer earlier (Zhou Wang) [1589697]
- [scsi] hisi_sas: make return type of prep functions void (Zhou Wang) [1589697]
- [scsi] hisi_sas: relocate smp sg map (Zhou Wang) [1589697]
- [scsi] hisi_sas: workaround a v3 hw hilink bug (Zhou Wang) [1589697]
- [scsi] hisi_sas: add readl poll timeout helper wrappers (Zhou Wang) [1589697]
- [scsi] hisi_sas: remove redundant handling to event95 for v3 (Zhou Wang) [1589697]
- [scsi] hisi_sas: config ATA de-reset as an constrained command for v3 hw (Zhou Wang) [1589697]
- [scsi] hisi_sas: update PHY linkrate after a controller reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: stop controller timer for reset (Zhou Wang) [1589697]
- [scsi] hisi_sas: check sas_dev gone earlier in hisi_sas_abort_task() (Zhou Wang) [1589697]
- [scsi] hisi_sas: fix PI memory size (Zhou Wang) [1589697]
- [scsi] hisi_sas: check host frozen before calling "done" function (Zhou Wang) [1589697]
- [scsi] hisi_sas: Add some checks to avoid free'ing a sas_task twice (Zhou Wang) [1589697]
- [scsi] hisi_sas: optimise the usage of DQ locking (Zhou Wang) [1589697]
- [scsi] hisi_sas: remove some unneeded structure members (Zhou Wang) [1589697]
- [scsi] hisi_sas: print device id for errors (Zhou Wang) [1589697]
- [scsi] hisi_sas: check IPTT is valid before using it for v3 hw (Zhou Wang) [1589697]
- [scsi] hisi_sas: consolidate command check in hisi_sas_get_ata_protocol() (Zhou Wang) [1589697]
- [scsi] hisi_sas: use dma_zalloc_coherent() (Zhou Wang) [1589697]
- [scsi] hisi_sas: delete timer when removing hisi_sas driver (Zhou Wang) [1589697]
- [scsi] hisi_sas: update RAS feature for later revision of v3 HW (Zhou Wang) [1589697]
- [scsi] hisi_sas: make SAS address of SATA disks unique (Zhou Wang) [1589697]
- [perf] vendor events arm64: Enable JSON events for ThunderX2 B0 (Robert Richter) [1487310]
- [perf] probe arm64: Fix symbol fixup issues due to ELF type (Robert Richter) [1487310]
- [init] init: fix false positives in W+X checking (Robert Richter) [1609244]
- [arm64] fix CONFIG_DEBUG_WX address reporting (Robert Richter) [1609244]

* Wed Aug 08 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-102.el7a]
- [mm] oom_reaper: gather each vma to prevent leaking TLB entry (Chris von Recklinghausen) [1554355] {CVE-2017-18202}
- [mm] swap: divide-by-zero when zero length swap file on ssd (Joe Lawrence) [1608970]
- [fs] cifs: handle USER_SESSION_DELETED the same way as NETWORK_SESSION_EXPIRED (Leif Sahlberg) [1589354]
- [netdrv] mlx5e: Set port trust mode to PCP as default (Alaa Hleihel) [1611135]
- [netdrv] ibmvnic: Fix error recovery on login failure (Steve Best) [1609815]
- [netdrv] ibmvnic: Revise RX/TX queue error messages (Steve Best) [1609815]
- [powerpc] powernv: Fix concurrency issue with npu->mmio_atsd_usage (Desnes Augusto Nunes do Rosario) [1611676]
- [powerpc] powernv: Fix save/restore of SPRG3 on entry/exit from stop (idle) (Gustavo Duarte) [1528600]
- [infiniband] rdma/hns: Set max_sge as minimal value of max_sq_sg and max_rq_sg (Zhou Wang) [1602022]

* Tue Jul 31 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-101.el7a]
- [redhat] configs: enable s390 auto expoline support (Hendrik Brueckner) [1578285]
- [redhat] spec: add gcc with expoline support (Hendrik Brueckner) [1578285]
- [s390] use expoline thunks in the BPF JIT (Hendrik Brueckner) [1588933]
- [s390] extend expoline to BC instructions (Hendrik Brueckner) [1588933]
- [s390] move spectre sysfs attribute code (Hendrik Brueckner) [1588933]
- [s390] kernel: use expoline for indirect branches (Hendrik Brueckner) [1588933]
- [s390] ftrace: use expoline for indirect branches (Hendrik Brueckner) [1588933]
- [s390] lib: use expoline for indirect branches (Hendrik Brueckner) [1588933]
- [s390] crc32-vx: use expoline for indirect branches (Hendrik Brueckner) [1588933]
- [s390] move expoline assembler macros to a header (Hendrik Brueckner) [1588933]
- [s390] add assembler macros for CPU alternatives (Hendrik Brueckner) [1588933]
- [s390] correct nospec auto detection init order (Hendrik Brueckner) [1578285]
- [s390] add sysfs attributes for spectre (Hendrik Brueckner) [1578285]
- [s390] report spectre mitigation via syslog (Hendrik Brueckner) [1578285]
- [s390] add automatic detection of the spectre defense (Hendrik Brueckner) [1578285]
- [s390] move nobp parameter functions to nospec-branch.c (Hendrik Brueckner) [1578285]
- [s390] do not bypass BPENTER for interrupt system calls (Hendrik Brueckner) [1578285]
- [net] ipv4: reset fnhe_mtu_locked after cache route flushed (Michael Cambria) [1599988]
- [net] ipv4: lock mtu in fnhe when received PMTU < net.ipv4.route.min_pmtu (Michael Cambria) [1599988]
- [net] ipv6: Do not consider linkdown nexthops during multipath (Hangbin Liu) [1597483]
- [net] sctp: handle two v4 addrs comparison in sctp_inet6_cmp_addr (Xin Long) [1597109]
- [net] sctp: do not check port in sctp_inet6_cmp_addr (Xin Long) [1597109]
- [net] avoid skb_warn_bad_offload on IS_ERR (Xin Long) [1597124]
- [net] rhashtable: Fix rhlist duplicates insertion (Xin Long) [1598675]

* Tue Jul 31 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-100.el7a]
- [redhat] configs: enable stack tracer and ftrace function_graph support for power9 (Steve Best) [1608035]
- [kernel] revert "sched/rt: Simplify the IPI based RT balancing logic" (Rafael Aquini) [1608423]
- [kernel] revert "sched/rt: Do not pull from current CPU if only one CPU to pull" (Rafael Aquini) [1608423]
- [kernel] revert "sched/rt: Use container_of() to get root domain in rto_push_irq_work_func()" (Rafael Aquini) [1608423]
- [kernel] revert "sched/rt: Up the root domain ref count when passing it around via IPIs" (Rafael Aquini) [1608423]
- [arm64] kernel: fix unwind_frame() for filtered out fn for function graph tracing (Jerome Marchand) [1354255]
- [proc] kcore: don't bounds check against address 0 (Jeremy Linton) [1601563]
- [char] ipmi_dmi: do not try to configure ipmi for HPE m400 (Tony Camuso) [1590373]
- [fs] xfs: enhance dinode verifier (Bill O'Donnell) [1574946] {CVE-2018-10322}
- [fs] xfs: move inode fork verifiers to xfs_dinode_verify (Bill O'Donnell) [1574946] {CVE-2018-10322}
- [fs] don't scan the inode cache before SB_BORN is set (Bill O'Donnell) [1549160]
- [fs] xfs: clear sb->s_fs_info on mount failure (Bill O'Donnell) [1549160]
- [fs] xfs: add mount delay debug option (Bill O'Donnell) [1549160]
- [pci] Add decoding for 16 GT/s link speed (Zhou Wang) [1509926]
- [pci] Disable MSI for HiSilicon Hip06/Hip07 only in Root Port mode (Zhou Wang) [1509926]
- [pci] portdrv: Compute MSI/MSI-X IRQ vectors after final allocation (Zhou Wang) [1509926]
- [pci] portdrv: Factor out Interrupt Message Number lookup (Zhou Wang) [1509926]
- [pci] portdrv: Consolidate comments (Zhou Wang) [1509926]
- [pci] portdrv: Add #defines for AER and DPC Interrupt Message Number masks (Zhou Wang) [1509926]
- [pci] pme: Handle invalid data when reading Root Status (Zhou Wang) [1509926]
- [pci] aer: Report non-fatal errors only to the affected endpoint (Zhou Wang) [1509926]
- [netdrv] cxgb4: Added missing break in ndo_udp_tunnel_{add/del} (Arjun Vynipadath) [1608356]
- [netdrv] cxgb4: do not return DUPLEX_UNKNOWN when link is down (Arjun Vynipadath) [1594126]
- [powerpc] powernv/mce: Don't silently restart the machine (Steve Best) [1608266]
- [infiniband] ib/rxe: avoid double kfree_skb (Jonathan Toppins) [1593883]
- [infiniband] iw_cxgb4: always set iw_cm_id.provider_data (Arjun Vynipadath) [1596519]
- [infiniband] iw_cxgb4: Fix an error handling path in 'c4iw_get_dma_mr()' (Arjun Vynipadath) [1596519]
- [infiniband] iw_cxgb4: Atomically flush per QP HW CQEs (Arjun Vynipadath) [1596519]
- [infiniband] rdma/cxgb4: release hw resources on device removal (Arjun Vynipadath) [1596519]

* Tue Jul 31 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-99.el7a]
- [scsi] sg: clean up gfp_mask in sg_build_indirect (Ming Lei) [1592371] {CVE-2018-1000204}
- [scsi] sg: allocate with __GFP_ZERO in sg_build_indirect() (Ming Lei) [1592371] {CVE-2018-1000204}
- [block] loop: Fix lost writes caused by missing flag (Ming Lei) [1561892]
- [block] blk-mq: avoid to synchronize rcu inside blk_cleanup_queue() (Ming Lei) [1592050]
- [block] blk-mq: remove synchronize_rcu() from blk_mq_del_queue_tag_set() (Ming Lei) [1592050]
- [block] blk-mq: introduce new lock for protecting hctx->dispatch_wait (Ming Lei) [1592050]
- [block] blk-mq: don't pass **hctx to blk_mq_mark_tag_wait() (Ming Lei) [1592050]
- [block] blk-mq: cleanup blk_mq_get_driver_tag() (Ming Lei) [1592050]
- [block] blk-mq: reinit q->tag_set_list entry only after grace period (Ming Lei) [1592050]
- [block] blk-mq: order getting budget and driver tag (Ming Lei) [1592050]
- [block] blk-mq: Reduce the number of if-statements in blk_mq_mark_tag_wait() (Ming Lei) [1592050]
- [block] blk-mq: improve tag waiting setup for non-shared tags (Ming Lei) [1592050]
- [block] blk-mq: fix issue with shared tag queue re-running (Ming Lei) [1592050]
- [block] blk-mq: put driver tag if dispatch budget can't be got (Ming Lei) [1592050]
- [block] blk-mq: don't allocate driver tag upfront for flush rq (Ming Lei) [1592050]
- [block] blk-mq: move blk_mq_put_driver_tag*() into blk-mq.h (Ming Lei) [1592050]
- [block] blk-mq-sched: decide how to handle flush rq via RQF_FLUSH_SEQ (Ming Lei) [1592050]
- [block] blk-flush: use blk_mq_request_bypass_insert() (Ming Lei) [1592050]
- [block] pass 'run_queue' to blk_mq_request_bypass_insert (Ming Lei) [1592050]
- [block] blk-flush: don't run queue for requests bypassing flush (Ming Lei) [1592050]
- [block] blk-mq: put the driver tag of nxt rq before first one is requeued (Ming Lei) [1592050]
- [block] blk-mq: don't handle failure in .get_budget (Ming Lei) [1592050]
- [block] scsi: don't get target/host busy_count in scsi_mq_get_budget() (Ming Lei) [1592050]
- [block] blk-mq: don't restart queue when .get_budget returns BLK_STS_RESOURCE (Ming Lei) [1592050]
- [block] scsi: implement .get_budget and .put_budget for blk-mq (Ming Lei) [1592050]
- [block] scsi: allow passing in null rq to scsi_prep_state_check() (Ming Lei) [1592050]
- [block] blk-mq-sched: improve dispatching from sw queue (Ming Lei) [1592050]
- [block] blk-mq: introduce .get_budget and .put_budget in blk_mq_ops (Ming Lei) [1592050]
- [block] block: kyber: check if there are requests in ctx in kyber_has_work() (Ming Lei) [1592050]
- [block] sbitmap: introduce __sbitmap_for_each_set() (Ming Lei) [1592050]
- [block] blk-mq-sched: move actual dispatching into one helper (Ming Lei) [1592050]
- [block] blk-mq-sched: dispatch from scheduler IFF progress is made in ->dispatch (Ming Lei) [1592050]

* Mon Jul 30 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-98.el7a]
- [redhat] arm64: Enable kernel support for ThunderX ZIP accelerator (Robert Richter) [1584203]
- [crypto] testmgr - Allow different compression results (Robert Richter) [1584203]
- [crypto] cavium - Fix smp_processor_id() warnings (Robert Richter) [1584203]
- [crypto] cavium - Fix statistics pending request value (Robert Richter) [1584203]
- [crypto] cavium - Prevent division by zero (Robert Richter) [1584203]
- [crypto] cavium - Limit result reading attempts (Robert Richter) [1584203]
- [crypto] cavium - Fix fallout from CONFIG_VMAP_STACK (Robert Richter) [1584203]
- [nvme] rdma: Use mr pool (David Milburn) [1552469 1488176]
- [nvme] rdma: Check remotely invalidated rkey matches our expected rkey (David Milburn) [1552469 1488176]
- [nvme] rdma: wait for local invalidation before completing a request (David Milburn) [1552469 1488176]
- [nvme] rdma: don't complete requests before a send work request has completed (David Milburn) [1552469 1488176]
- [nvme] rdma: don't suppress send completions (David Milburn) [1552469 1488176]
- [scsi] megaraid_sas: driver version upgrade (Tomas Henzl) [1520419]
- [scsi] megaraid_sas: Do not do Kill adapter if GET_CTRL_INFO times out (Tomas Henzl) [1520419]
- [scsi] megaraid_sas: Increase timeout by 1 sec for non-RAID fastpath IOs (Tomas Henzl) [1520419]
- [scsi] mpt3sas: driver version upgrade (Tomas Henzl) [1520436]
- [scsi] mpt3sas: fix oops in error handlers after shutdown/unload (Tomas Henzl) [1520436]
- [scsi] mpt3sas: Fix IO error occurs on pulling out a drive from RAID1 volume created on two SATA drive (Tomas Henzl) [1520436]
- [scsi] mpt3sas: Fix removal and addition of vSES device during host reset (Tomas Henzl) [1520436]
- [scsi] scsi: mpt3sas: Processing of Cable Exception events (Tomas Henzl) [1520436]

* Mon Jul 30 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-97.el7a]
- [arm64] Get rid of __smccc_workaround_1_hvc_* (Andrew Jones) [1550878]
- [arm64] Enable ARM64_HARDEN_EL2_VECTORS on Cortex-A57 and A72 (Andrew Jones) [1550878]
- [arm64] kvm: Allow mapping of vectors outside of the RAM region (Andrew Jones) [1550878]
- [arm64] Make BP hardening slot counter available (Andrew Jones) [1550878]
- [arm64] arm/arm64: kvm: Introduce EL2-specific executable mappings (Andrew Jones) [1550878]
- [arm64] kvm: Allow far branches from vector slots to the main vectors (Andrew Jones) [1550878]
- [arm64] kvm: Reserve 4 additional instructions in the BPI template (Andrew Jones) [1550878]
- [arm64] kvm: Move BP hardening vectors into .hyp.text section (Andrew Jones) [1550878]
- [arm64] kvm: Move stashing of x0/x1 into the vector code itself (Andrew Jones) [1550878]
- [arm64] kvm: Move vector offsetting from hyp-init.S to kvm_get_hyp_vector (Andrew Jones) [1550878]
- [arm64] Update the KVM memory map documentation (Andrew Jones) [1550878]
- [arm64] fix documentation on kernel pages mappings to HYP VA (Andrew Jones) [1550878]
- [arm64] kvm: Introduce EL2 VA randomisation (Andrew Jones) [1550878]
- [arm64] kvm: Dynamically compute the HYP VA mask (Andrew Jones) [1550878]
- [arm64] insn: Allow ADD/SUB (immediate) with LSL #12 (Andrew Jones) [1550878]
- [arm64] arm64; insn: Add encoder for the EXTR instruction (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Move HYP IO VAs to the "idmap" range (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Fix HYP unmapping going off limits (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Fix idmap size and alignment (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Keep GICv2 HYP VAs in kvm_vgic_global_state (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Move ioremap calls to create_hyp_io_mappings (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Demote HYP VA range display to being a debug feature (Andrew Jones) [1550878]
- [arm64] kvm: arm/arm64: Do not use kern_hyp_va() with kvm_vgic_global_state (Andrew Jones) [1550878]
- [arm64] cpufeatures: Drop the ARM64_HYP_OFFSET_LOW feature flag (Andrew Jones) [1550878]
- [arm64] kvm: Dynamically patch the kernel/hyp VA mask (Andrew Jones) [1550878]
- [arm64] insn: Add encoder for bitwise operations using literals (Andrew Jones) [1550878]
- [arm64] insn: Add N immediate encoding (Andrew Jones) [1550878]
- [arm64] alternatives: Add dynamic patching feature (Andrew Jones) [1550878]

* Thu Jul 26 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-96.el7a]
- [powerpc] ocxl: Add an IOCTL so userspace knows what OCXL features are available (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] ocxl: Rename pnv_ocxl_spa_remove_pe to clarify it's action (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] ocxl: Fix page fault handler in case of fault on dying process (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] ocxl: Fix missing unlock on error in afu_ioctl_enable_p9_wait() (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] ocxl: Expose the thread_id needed for wait on POWER9 (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] ocxl: Document new OCXL IOCTLs (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] ocxl: Document the OCXL_IOCTL_GET_METADATA IOCTL (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] use task_pid_nr() for TID allocation (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] kernel: Block interrupts when updating TIDR (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] Use TIDR CPU feature to control TIDR allocation (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] Add TIDR CPU feature for POWER9 (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] misc: ocxl: use put_device() instead of device_unregister() (Desnes Augusto Nunes do Rosario) [1600643]
- [powerpc] powerpc64/ftrace: Implement support for ftrace_regs_caller() (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Use the generic version of ftrace_replace_code() (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/module: Tighten detection of mcount call sites with -mprofile-kernel (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/kexec: Hard disable ftrace before switching to the new kernel (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Disable ftrace during kvm entry/exit (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Disable ftrace during hotplug (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Delay enabling ftrace on secondary cpus (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Add helpers to hard disable ftrace (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Rearrange #ifdef sections in ftrace.h (Gustavo Duarte) [1580475]
- [powerpc] powerpc64/ftrace: Add a field in paca to disable ftrace in unsafe code paths (Gustavo Duarte) [1580475]
- [powerpc] smp_send_stop do not offline stopped CPUs (Gustavo Duarte) [1568349]
- [powerpc] powernv: Fix NVRAM sleep in invalid context when crashing (Gustavo Duarte) [1568349]
- [powerpc] powernv: Fix opal_event_shutdown() called with interrupts disabled (Gustavo Duarte) [1568349]
- [powerpc] powernv: Fix OPAL NVRAM driver OPAL_BUSY loops (Gustavo Duarte) [1568349]
- [powerpc] powernv: Make opal_event_shutdown() callable from IRQ context (Gustavo Duarte) [1568349]
- [powerpc] Fix deadlock with multiple calls to smp_send_stop (Gustavo Duarte) [1568349]
- [powerpc] Fix smp_send_stop NMI IPI handling (Gustavo Duarte) [1568349]
- [powerpc] powernv: Always stop secondaries before reboot/shutdown (Gustavo Duarte) [1568349]
- [powerpc] hard disable irqs in smp_send_stop loop (Gustavo Duarte) [1568349]
- [powerpc] use NMI IPI for smp_send_stop (Gustavo Duarte) [1568349]

* Wed Jul 25 2018 Augusto Caringi <acaringi@redhat.com> [4.14.0-95.el7a]
- [scsi] libsas: add transport class for ATA devices (Xiaojun Tan) [1597962]
- [scsi] libsas: defer ata device eh commands to libata (Xiaojun Tan) [1597962]
- [scsi] ata: do not schedule hot plug if it is a sas host (Xiaojun Tan) [1597962]
- [scsi] libsas: Fix kernel-doc headers (Xiaojun Tan) [1597962]
- [scsi] libsas: notify event PORTE_BROADCAST_RCVD in sas_enable_revalidation() (Xiaojun Tan) [1597962]
- [scsi] lpfc: Revise copyright for new company language (Dick Kennedy) [1595382]
- [scsi] lpfc: update driver version to 12.0.0.5 (Dick Kennedy) [1595382]
- [scsi] lpfc: devloss timeout race condition caused null pointer reference (Dick Kennedy) [1595382]
- [scsi] lpfc: Fix NVME Target crash in defer rcv logic (Dick Kennedy) [1595382]
- [scsi] lpfc: Support duration field in Link Cable Beacon V1 command (Dick Kennedy) [1595382]
- [scsi] lpfc: Make PBDE optimizations configurable (Dick Kennedy) [1595382]
- [scsi] lpfc: Fix abort error path for NVMET (Dick Kennedy) [1595382]
- [scsi] lpfc: Fix panic if driver unloaded when port is offline (Dick Kennedy) [1595382]
- [scsi] lpfc: Fix driver not setting dpp bits correctly in doorbell word (Dick Kennedy) [1595382]
- [scsi] lpfc: Add Buffer overflow check, when nvme_info larger than PAGE_SIZE (Dick Kennedy) [1595382]
- [scsi] lpfc: use monotonic timestamps for statistics (Dick Kennedy) [1595382]

* Fri Jul 20 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-94.el7a]
- [netdrv] cxgb4: assume flash part size to be 4MB, if it can't be determined (Arjun Vynipadath) [1600589]
- [netdrv] cxgb4: Support ethtool private flags (Arjun Vynipadath) [1529041]
- [netdrv] cxgb4: Add support for FW_ETH_TX_PKT_VM_WR (Arjun Vynipadath) [1529041]
- [netdrv] cxgb4: do not fail vf instatiation in slave mode (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4/cxgb4vf: Notify link changes to OS-dependent code (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: Add FORCE_PAUSE bit to 32 bit port caps (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: fix offset in collecting TX rate limit info (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: Check for kvzalloc allocation failure (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4/cxgb4vf: link management changes for new SFP (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: do L1 config when module is inserted (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: change the port capability bits definition (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: Correct ntuple mask validation for hash filters (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: fix the wrong conversion of Mbps to Kbps (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: copy mbox log size to PF0-3 adap instances (Arjun Vynipadath) [1596516]
- [netdrv] cxgb4: zero the HMA memory (Arjun Vynipadath) [1596516]
- [crypto] chelsio: Remove separate buffer used for DMA map B0 block in CCM (Arjun Vynipadath) [1596543]
- [crypto] chelsio: Send IV as Immediate for cipher algo (Arjun Vynipadath) [1596543]
- [crypto] chelsio: request to HW should wrap (Arjun Vynipadath) [1596543]
- [kernel] kprobes: Propagate error from disarm_kprobe_ftrace() (Josh Poimboeuf) [1600845]
- [kernel] kprobes: Propagate error from arm_kprobe_ftrace() (Josh Poimboeuf) [1600845]
- [kernel] x86/bugs: Expose /sys/../spec_store_bypass (Gustavo Duarte) [1597392]
- [cpufreq] governor: Ensure sufficiently large sampling intervals (Steve Best) [1603112]
- [powerpc] perf/imc: Fix nest-imc cpuhotplug callback failure (Steve Best) [1601703]

* Fri Jul 20 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-93.el7a]
- [arm64] acpi / pptt: use ACPI ID whenever ACPI_PPTT_ACPI_PROCESSOR_ID_VALID is set (Xiaojun Tan) [1582176]
- [arm64] topology: Avoid checking numa mask for scheduler MC selection (Xiaojun Tan) [1582176]
- [arm64] topology: divorce MC scheduling domain from core_siblings (Xiaojun Tan) [1582176]
- [arm64] acpi: Add PPTT to injectable table list (Xiaojun Tan) [1582176]
- [arm64] topology: enable ACPI/PPTT based CPU topology (Xiaojun Tan) [1582176]
- [arm64] topology: rename cluster_id (Xiaojun Tan) [1582176]
- [arm64] Add support for ACPI based firmware tables (Xiaojun Tan) [1582176]
- [arm64] base cacheinfo: Add support for ACPI based firmware tables (Xiaojun Tan) [1582176]
- [arm64] acpi: Enable PPTT support on ARM64 (Xiaojun Tan) [1582176]
- [arm64] acpi/pptt: Add Processor Properties Topology Table parsing (Xiaojun Tan) [1582176]
- [arm64] acpi: Create arch specific cpu to acpi id helper (Xiaojun Tan) [1582176]
- [arm64] cacheinfo: rename of_node to fw_token (Xiaojun Tan) [1582176]
- [arm64] base: cacheinfo: setup DT cache properties early (Xiaojun Tan) [1582176]
- [arm64] base: cacheinfo: move cache_setup_of_node() (Xiaojun Tan) [1582176]
- [arm64] base: cacheinfo: fix cache type for non-architected system cache (Xiaojun Tan) [1582176]
- [arm64] acpica: acpi 6.2: Additional PPTT flags (Xiaojun Tan) [1582176]
- [arm64] revert "do not upstream - topology: Adjust sysfs topology" (Xiaojun Tan) [1582176]
- [arm64] revert "base: cacheinfo: let arm64 provide cache info without using DT or ACPI" (Xiaojun Tan) [1582176]

* Mon Jul 16 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-92.el7a]
- [infiniband] rdma/ucma: Don't allow setting RDMA_OPTION_IB_PATH without an RDMA device (Jonathan Toppins) [1593883]
- [infiniband] rdma/core: Avoid that ib_drain_qp() triggers an out-of-bounds stack access (Jonathan Toppins) [1593883]
- [infiniband] rdma/ucma: Allow resolving address w/o specifying source address (Jonathan Toppins) [1593883]
- [infiniband] ib/umem: Use the correct mm during ib_umem_release (Jonathan Toppins) [1593883]
- [infiniband] ib/core: Honor port_num while resolving GID for IB link layer (Jonathan Toppins) [1593883]
- [infiniband] ib/rxe: add RXE_START_MASK for rxe_opcode IB_OPCODE_RC_SEND_ONLY_INV (Jonathan Toppins) [1593883]
- [infiniband] ib/core: Make ib_mad_client_id atomic (Jonathan Toppins) [1593883]
- [infiniband] rdma/cma: Do not query GID during QP state transition to RTR (Jonathan Toppins) [1593883]
- [net] xprtrdma: Fix list corruption / DMAR errors during MR recovery (Jonathan Toppins) [1593883]
- [net] xprtrdma: Fix corner cases when handling device removal (Jonathan Toppins) [1593883]
- [net] xprtrdma: Fix latency regression on NUMA NFS/RDMA clients (Jonathan Toppins) [1593883]
- [infiniband] ib/core: Fix error code for invalid GID entry (Jonathan Toppins) [1593883]
- [infiniband] rdma/iwpm: fix memory leak on map_info (Jonathan Toppins) [1593883]
- [infiniband] ib/ipoib: fix ipoib_start_xmit()'s return type (Jonathan Toppins) [1593883]
- [infiniband] ib/nes: fix nes_netdev_start_xmit()'s return type (Jonathan Toppins) [1593883]
- [infiniband] rdma/cma: Fix use after destroy access to net namespace for IPoIB (Jonathan Toppins) [1593883]
- [infiniband] ib/uverbs: Fix validating mandatory attributes (Jonathan Toppins) [1593883]
- [infiniband] ib/rxe: Fix for oops in rxe_register_device on ppc64le arch (Jonathan Toppins) [1593883]
- [infiniband] ib/core: Fix comments of GID query functions (Jonathan Toppins) [1593883]
- [infiniband] ib/srp: Fix IPv6 address parsing (Jonathan Toppins) [1593883]
- [infiniband] ib/srpt: Fix an out-of-bounds stack access in srpt_zerolength_write() (Jonathan Toppins) [1593883]
- [infiniband] rdma/rxe: Fix an out-of-bounds read (Jonathan Toppins) [1593883]
- [infiniband] ib/srp: Fix srp_abort() (Jonathan Toppins) [1593883]
- [infiniband] ib/srp: Fix completion vector assignment algorithm (Jonathan Toppins) [1593883]

* Sat Jul 14 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-91.el7a]
- [redhat] spec: compress modules with xz on all architectures ("Herton R. Krzesinski") [1486850]
- [iommu] update dmi iommu passthrough check on eMAG systems (Iyappan Subramanian) [1579910]
- [scsi] aacraid: Fix PD performance regression over incorrect qd being set (Raghava Aditya Renukunta) [1592986]
- [scsi] ibmvfc: Avoid unnecessary port relogin (Steve Best) [1592789]
- [scsi] qla2xxx: Mask off Scope bits in retry delay (Himanshu Madhani) [1588134]
- [scsi] ipr: Format HCAM overlay ID 0x41 (Desnes Augusto Nunes do Rosario) [1594391]
- [s390] scsi: zfcp: fix infinite iteration on ERP ready list (Hendrik Brueckner) [1597213]
- [s390] ptrace: add runtime instrumention register get/set (Hendrik Brueckner) [1546200]
- [s390] runtime_instrumentation: clean up struct runtime_instr_cb (Hendrik Brueckner) [1546200]
- [s390] ptrace: fix guarded storage regset handling (Hendrik Brueckner) [1546200]
- [s390] archrandom: Rework arch random implementation (Hendrik Brueckner) [1594252]
- [s390] archrandom: Reconsider s390 arch random implementation (Hendrik Brueckner) [1594252]
- [kernel] sched/rt: Up the root domain ref count when passing it around via IPIs (Steve Best) [1585419]
- [kernel] sched/rt: Use container_of() to get root domain in rto_push_irq_work_func() (Steve Best) [1585419]
- [kernel] sched/rt: Do not pull from current CPU if only one CPU to pull (Steve Best) [1585419]
- [kernel] sched/rt: Simplify the IPI based RT balancing logic (Steve Best) [1585419]
- [powerpc] vphn: Improve recognition of PRRN/VPHN (Desnes Augusto Nunes do Rosario) [1544436]
- [powerpc] hotplug: Improve responsiveness of hotplug change (Desnes Augusto Nunes do Rosario) [1544436]
- [powerpc] vphn: Update CPU topology when VPHN enabled (Desnes Augusto Nunes do Rosario) [1544436]
- [powerpc] vphn: Fix numa update end-loop bug (Desnes Augusto Nunes do Rosario) [1544436]

* Wed Jul 04 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-90.el7a]
- [redhat] configs: enable HiSilicon HIP08 ROCE driver (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add 64KB page size support for hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix the bug with NULL pointer (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set NULL for __internal_mr (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Enable inner_pa_vld filed of mpt (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set desc_dma_addr for zero when free cmq desc (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix the bug with rq sge (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Not support qp transition from reset to reset for hip06 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add return operation when configured global param fail (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update convert function of endian format (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Load the RoCE dirver automatically (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Bugfix for rq record db for kernel (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add rq inline flags judgement (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix a couple misspellings (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Submit bad wr (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update assignment method for owner field of send wqe (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Adjust the order of cleanup hem table (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Only assign dqpn if IB_QP_PATH_DEST_QPN bit is set (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Remove some unnecessary attr_mask judgement (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Only assign mtu if IB_QP_PATH_MTU bit is set (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix the qp context state diagram (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Intercept illegal RDMA operation when use inline data (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Bugfix for init hem table (Zhou Wang) [1557402]
- [infiniband] rdma/hns: ensure for-loop actually iterates and free's buffers (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix cq record doorbell enable in kernel (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix init resp when alloc ucontext (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Use structs to describe the uABI instead of opencoding (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix cqn type and init resp (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Support cq record doorbell for kernel space (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Support rq record doorbell for kernel space (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Support cq record doorbell for the user space (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Support rq record doorbell for the user space (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Replace __raw_write*(cpu_to_le*()) with LE write*() (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Use free_pages function instead of free_page (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix QP state judgement before receiving work requests (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix a bug with modifying mac address (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix the endian problem for hns (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix misplaced call to hns_roce_cleanup_hem_table (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add names to function arguments in function pointers (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Remove unnecessary operator (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Remove unnecessary platform_get_resource() error check (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set the guid for hip08 RoCE device (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update the verbs of polling for completion (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Assign zero for pkey_index of wc in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fill sq wqe context of ud type in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add gsi qp support for modifying qp in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Create gsi qp in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Assign the correct value for tx_cqn (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix endian problems around imm_data and rkey (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Assign dest_qp when deregistering mr (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix QP state judgement before sending work requests (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Filter for zero length of sge in hip08 kernel mode (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set access flags of hip08 RoCE (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update the usage of sr_max and rr_max field (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add rq inline data support for hip08 RoCE (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add detailed comments for mb() call (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add eq support of hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Refactor eq code for hip06 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Get rid of page operation after dma_alloc_coherent (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Get rid of virt_to_page and vmap calls after dma_alloc_coherent (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix the issue of IOVA not page continuous in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Modify the usage of cmd_sn in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Unify the calculation for hem index in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set the owner field of SQWQE in hip08 RoCE (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add sq_invld_flg field in QP context (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update the usage of ack timeout in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set sq_cur_sge_blk_addr field in QPC in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Enable the cqe field of sqwqe of RC (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set se attribute of sqwqe in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Configure fence attribute in hip08 RoCE (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Configure TRRL field in hip08 RoCE device (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update calculation of irrl_ba field for hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Configure sgid type for hip08 RoCE (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Generate gid type of RoCEv2 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add rereg mr support for hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add modify CQ support for hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update the PD&CQE&MTT specification in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update the IRRL table chunk size in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Support WQE/CQE/PBL page size configurable feature in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: fix spelling mistake: "Reseved" -> "Reserved" (Zhou Wang) [1557402]
- [infiniband] ib/hns: Declare local functions 'static' (Zhou Wang) [1557402]
- [infiniband] ib/hns: Annotate iomem pointers correctly (Zhou Wang) [1557402]
- [infiniband] rdma/hns: return 0 rather than return a garbage status value (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix calltrace for sleeping in atomic (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Don't unregister a callback we didn't register (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Avoid NULL pointer exception (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Set rdma_ah_attr type for querying qp (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Only assign dest_qp if IB_QP_DEST_QPN bit is set (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Check return value of kzalloc (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Refactor code for readability (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Modify the value with rd&dest_rd of qp_attr (Zhou Wang) [1557402]
- [infiniband] rdma/hns: remove redundant assignment to variable j (Zhou Wang) [1557402]
- [infiniband] rdma/hns: make various function static, fixes warnings (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Delete the unnecessary initializing enum to zero (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Fix inconsistent warning (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Replace condition statement using hardware version information (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add releasing resource operation in error branch (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Configure the MTPT in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add support for processing send wr and receive wr (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add QP operations support for hip08 SoC (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add CQ operations support for hip08 RoCE driver (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Configure mac&gid and user access region for hip08 RoCE driver (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Support multi hop addressing for PBL in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Split CQE from MTT in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Update the interfaces for MTT/CQE multi hop addressing in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Configure BT BA and BT attribute for the contexts in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add the interfaces to support multi hop addressing for the contexts in hip08 (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add mailbox's implementation for hip08 RoCE driver (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add profile support for hip08 driver (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Add command queue support for hip08 RoCE driver (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Modify assignment device variable to support both PCI device and platform device (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Initialize the PCI device for hip08 RoCE (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Move priv in order to add multiple hns_roce support (Zhou Wang) [1557402]
- [infiniband] rdma/hns: Split hw v1 driver from hns roce driver (Zhou Wang) [1557402]

* Mon Jul 02 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-89.el7a]
- [redhat] configs: build IMA and the TPM device drivers into the PPC kernel (Gustavo Duarte) [1567759]
- [iommu] force IOMMU passthrough mode for Ampere eMAG system (Iyappan Subramanian) [1579910]
- [acpi] acpi / cppc: Fix invalid PCC channel status errors (Al Stone) [1590007]
- [acpi] acpi / cppc: Check for valid PCC subspace only if PCC is used (Al Stone) [1590007]
- [acpi] acpi / cppc: Add support for CPPC v3 (Al Stone) [1590007]
- [acpi] acpi / cppc: Update all pr_(debug/err) messages to log the susbspace id (Al Stone) [1590007]
- [mm] oom_reaper: fix memory corruption (Jerome Marchand) [1520351]
- [mm] userfaultfd: clear the vma->vm_userfaultfd_ctx if UFFD_EVENT_FORK fails (Andrea Arcangeli) [1499459]

* Fri Jun 29 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-88.el7a]
- [net] ipv6: Reflect MTU changes on PMTU of exceptions for MTU-less routes (Stefano Brivio) [1540801]
- [net] socket: close race condition between sock_close() and sockfs_setattr() (Hangbin Liu) [1591837] {CVE-2018-12232}
- [net] vti6: Change minimum MTU to IPV4_MIN_MTU, vti6 can carry IPv4 too (Ravi Aysola) [1576498]
- [net] ipv4: igmp: guard against silly MTU values (Ravi Aysola) [1576498]
- [net] xfrm: don't call xfrm_policy_cache_flush while holding spinlock (Herbert Xu) [1554210]
- [net] use skb_is_gso_sctp() instead of open-coding (Xin Long) [1555193]
- [net] bpf: fix bpf_skb_adjust_net/bpf_skb_proto_xlat to deal with gso sctp skbs (Xin Long) [1555193]
- [net] docs: segmentation-offloads.txt: add SCTP info (Xin Long) [1555193]
- [net] gso: validate gso_type in GSO handlers (Xin Long) [1555193]
- [net] vti6: Fix dev->max_mtu setting (Stefano Brivio) [1557277]
- [net] vti6: Keep set MTU on link creation or change, validate it (Stefano Brivio) [1557271]
- [net] ipvs: remove IPS_NAT_MASK check to fix passive FTP (Florian Westphal) [1545025]
- [net] bonding: process the err returned by dev_set_allmulti properly in bond_enslave (Xin Long) [1561430]
- [net] bonding: move dev_mc_sync after master_upper_dev_link in bond_enslave (Xin Long) [1561430]
- [net] bonding: fix the err path for dev hwaddr sync in bond_enslave (Xin Long) [1561430]
- [net] netfilter: ebtables: fix erroneous reject of last rule (Florian Westphal) [1552368] {CVE-2018-1068}
- [net] netfilter: ebtables: CONFIG_COMPAT: don't trust userland offsets (Florian Westphal) [1552368] {CVE-2018-1068}
- [net] netfilter: bridge: ebt_among: add more missing match size checks (Florian Westphal) [1552368] {CVE-2018-1068}
- [net] netfilter: bridge: ebt_among: add missing match size checks (Florian Westphal) [1552368] {CVE-2018-1068}
- [net] xfrm: reuse uncached_list to track xdsts (Xin Long) [1540869]

* Fri Jun 22 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-87.el7a]
- [redhat] spec: remove extra dot in kernel-devel post ("Herton R. Krzesinski") [1588730]
- [netdrv] pppoe: take ->needed_headroom of lower device into account on xmit (Florian Westphal) [1549424]
- [netdrv] igb: Free IRQs when device is hotplugged (Corinna Vinschen) [1592419]
- [netdrv] ixgbevf: Free IRQ when PCI error recovery removes the device (Ken Cox) [1586016]
- [netdrv] wil6210: missing length check in wmi_set_ie (Stanislaw Gruszka) [1590843] {CVE-2018-5848}
- [nvme] don't send keep-alives to the discovery controller (David Milburn) [1586325]
- [fs] nfsv4: Fix possible 1-byte stack overflow in nfs_idmap_read_and_verify_message (Dave Wysochanski) [1592884]
- [pm] core: fix deferred probe breaking suspend resume order (Iyappan Subramanian) [1549771]
- [tty] pl011: Avoid spuriously stuck-off interrupts (Andrew Jones) [1540531]
- [s390] kvm: s390: vsie: fix < 8k check for the itdba (Thomas Huth) [1592889]
- [s390] kvm: s390: fix memory overwrites when not using SCA entries (Thomas Huth) [1592889]
- [s390] kvm: s390: provide io interrupt kvm_stat (Thomas Huth) [1592889]
- [s390] kvm: s390: vsie: use READ_ONCE to access some SCB fields (Thomas Huth) [1592889]
- [s390] kvm: s390: use created_vcpus in more places (Thomas Huth) [1592889]
- [s390] kvm: s390: add proper locking for CMMA migration bitmap (Thomas Huth) [1592889]
- [s390] kvm: s390: prevent buffer overrun on memory hotplug during migration (Thomas Huth) [1592889]
- [s390] kvm: s390: fix cmma migration for multiple memory slots (Thomas Huth) [1592889]
- [powerpc] rtc: opal: Fix OPAL RTC driver OPAL_BUSY loops (Steve Best) [1593301]
- [powerpc] rtc-opal: Fix handling of firmware error codes, prevent busy loops (Steve Best) [1593301]
- [powerpc] powernv: define a standard delay for OPAL_BUSY type retry loops (Steve Best) [1593301]

* Fri Jun 22 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-86.el7a]
- [scsi] smartpqi: update driver version (Don Brace) [1593746]
- [scsi] smartpqi: fix critical ARM issue reading PQI index registers (Don Brace) [1593746]
- [scsi] smartpqi: workaround fw bug for oq deletion (Don Brace) [1593746]
- [scsi] smartpqi: allow static build ("built-in") (Don Brace) [1593746]
- [scsi] lpfc: update driver version to 12.0.0.4 (Dick Kennedy) [1584326]
- [scsi] lpfc: Fix port initialization failure (Dick Kennedy) [1584326]
- [scsi] lpfc: Fix 16gb hbas failing cq create (Dick Kennedy) [1584326]
- [scsi] lpfc: Fix crash in blk_mq layer when executing modprobe -r lpfc (Dick Kennedy) [1584326]
- [scsi] lpfc: correct oversubscription of nvme io requests for an adapter (Dick Kennedy) [1584326]
- [scsi] lpfc: Fix MDS diagnostics failure (Rx < Tx) (Dick Kennedy) [1584326]
- [scsi] lpfc: fix spelling mistakes: "mabilbox" and "maibox" (Dick Kennedy) [1584326]
- [scsi] lpfc: Comment cleanup regarding Broadcom copyright header (Dick Kennedy) [1584326]
- [scsi] lpfc: update driver version to 12.0.0.3 (Dick Kennedy) [1584326]
- [scsi] lpfc: Enhance log messages when reporting CQE errors (Dick Kennedy) [1584326]
- [scsi] lpfc: Fix up log messages and stats counters in IO submit code path (Dick Kennedy) [1584326]
- [scsi] lpfc: Driver NVME load fails when CPU cnt > WQ resource cnt (Dick Kennedy) [1584326]
- [scsi] lpfc: Handle new link fault code returned by adapter firmware (Dick Kennedy) [1584326]
- [scsi] lpfc: Correct fw download error message (Dick Kennedy) [1584326]
- [scsi] lpfc: enhance LE data structure copies to hardware (Dick Kennedy) [1584326]
- [scsi] lpfc: Change IO submit return to EBUSY if remote port is recovering (Dick Kennedy) [1584326]

* Thu Jun 21 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-85.el7a]
- [powerpc] kvm: ppc: book3s hv: Work around TEXASR bug in fake suspend state (Suraj Jitindar Singh) [1517546]
- [powerpc] kvm: ppc: book3s hv: Work around XER[SO] bug in fake suspend mode (Suraj Jitindar Singh) [1517546]
- [powerpc] kvm: ppc: book3s hv: Work around transactional memory bugs in POWER9 (Suraj Jitindar Singh) [1517546]
- [powerpc] powernv: Provide a way to force a core into SMT4 mode (Suraj Jitindar Singh) [1517546]
- [powerpc] Add CPU feature bits for TM bug workarounds on POWER9 v2.2 (Suraj Jitindar Singh) [1517546]
- [powerpc] Free up CPU feature bits on 64-bit machines (Suraj Jitindar Singh) [1517546]
- [powerpc] book e: Remove unused CPU_FTR_L2CSR bit (Suraj Jitindar Singh) [1517546]
- [powerpc] Use feature bit for RTC presence rather than timebase presence (Suraj Jitindar Singh) [1517546]
- [powerpc] 64s: Fix Power9 DD2.1 logic in DT CPU features (Suraj Jitindar Singh) [1517546]
- [powerpc] 64s: Fix Power9 DD2.0 workarounds by adding DD2.1 feature (Suraj Jitindar Singh) [1517546]
- [powerpc] 64s/idle: avoid POWER9 DD1 and DD2.0 PMU workaround on DD2.1 (Suraj Jitindar Singh) [1517546]
- [powerpc] 64s/idle: avoid POWER9 DD1 and DD2.0 ERAT workaround on DD2.1 (Suraj Jitindar Singh) [1517546]
- [powerpc] add POWER9_DD20 feature (Suraj Jitindar Singh) [1517546]
- [powerpc] 64: Free up CPU_FTR_ICSWX (Suraj Jitindar Singh) [1517546]

* Mon Jun 18 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-84.el7a]
- [redhat] configs: Enable HiSilicon HIP08 perf driver (Zhou Wang) [1510280]
- [perf] hisi: Documentation for HiSilicon SoC PMU driver (Zhou Wang) [1510280]
- [perf] hisi: Add support for HiSilicon SoC DDRC PMU driver (Zhou Wang) [1510280]
- [perf] hisi: Add support for HiSilicon SoC HHA PMU driver (Zhou Wang) [1510280]
- [perf] hisi: Add support for HiSilicon SoC L3C PMU driver (Zhou Wang) [1510280]
- [perf] hisi: Add support for HiSilicon SoC uncore PMU driver (Zhou Wang) [1510280]
- [mm] mempolicy: add nodes_empty check in SYSC_migrate_pages (Xiaojun Tan) [1466051]
- [mm] mempolicy: fix the check of nodemask from user (Xiaojun Tan) [1466051]
- [mm] mempolicy: remove redundant check in get_nodes (Xiaojun Tan) [1466051]
- [mm] proc: do not access cmdline nor environ from file-backed areas (Oleg Nesterov) [1576340] {CVE-2018-1120}
- [scsi] sr: pass down correctly sized SCSI sense buffer ("Ewan D. Milne") [1583617] {CVE-2018-11506}
- [kernel] perf/hwbp: Simplify the perf-hwbp code, fix documentation (Eugene Syromiatnikov) [1569875] {CVE-2018-1000199}

* Thu Jun 14 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-83.el7a]
- [scsi] aacraid: Correct hba_send to include iu_type (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Insure command thread is not recursively stopped (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: fix typos in printk (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Auto detect INTx or MSIx mode during sync cmd processing (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Preserve MSIX mode in the OMR register (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Implement DropIO sync command (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: fix shutdown crash when init fails (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Delay for rescan worker needs to be 10 seconds (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Get correct lun count (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: remove redundant setting of variable c (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Fix driver oops with dead battery (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Update driver version to 50877 (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Remove AAC_HIDE_DISK check in queue command (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Remove unused rescan variable (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Skip schedule rescan in case of kdump (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Fix hang while scanning in eh recovery (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Reschedule host scan in case of failure (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Use hotplug handling function in place of scsi_scan_host (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Block concurrent hotplug event handling (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Merge adapter setup with resolve luns (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Refactor resolve luns code and scsi functions (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Added macros to help loop through known buses and targets (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Process hba and container hot plug events in single function (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Merge func to get container information (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Add helper function to set queue depth (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Save bmic phy information for each phy (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Create helper functions to get lun info (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Move function around to match existing code (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Untangle targets setup from report phy luns (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Add target setup helper function (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Refactor and rename to make mirror existing changes (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Change phy luns function to use common bmic function (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Create bmic submission function from bmic identify (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Move code to wait for IO completion to shutdown func (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Refactor reset_host store function (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Allow reset_host sysfs var to recover Panicked Fw (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: remove unused variable managed_request_id (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: address UBSAN warning regression (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Prevent crash in case of free interrupt during scsi EH path (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Perform initialization reset only once (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: Check for PCI state of device in a generic way (Raghava Aditya Renukunta) [1525240]
- [scsi] aacraid: use timespec64 instead of timeval (Raghava Aditya Renukunta) [1525240]

* Thu Jun 14 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-82.el7a]
- [s390] cpum_sf: ensure sample frequency of perf event attributes is non-zero (Hendrik Brueckner) [1583199]
- [virt] kvm: arm/arm64: vgic: Kick new VCPU on interrupt migration (Auger Eric) [1573182]
- [virt] kvm: arm/arm64: vgic-its: Fix potential overrun in vgic_copy_lpi_list (Auger Eric) [1573182]
- [virt] kvm: arm/arm64: vgic: Disallow Active+Pending for level interrupts (Auger Eric) [1573182]
- [virt] kvm: arm/arm64: vgic-v3: Tighten synchronization for guests using v2 on v3 (Auger Eric) [1573182]
- [virt] kvm: arm/arm64: Reduce verbosity of KVM init log (Auger Eric) [1573182]
- [virt] kvm: arm/arm64: vgic: Add missing irq_lock to vgic_mmio_read_pending (Auger Eric) [1573182]
- [block] blk_rq_map_user_iov: fix error override (Ming Lei) [1524239]
- [block] fix blk_rq_append_bio (Ming Lei) [1524239]
- [block] don't let passthrough IO go into .make_request_fn() (Ming Lei) [1524239]
- [block] null_blk: fix 'Invalid parameters' when loading module (Ming Lei) [1550911]
- [block] pass inclusive 'lend' parameter to truncate_inode_pages_range (Ming Lei) [1516190]
- [block] Invalidate cache on discard v2 (Ming Lei) [1516190]
- [redhat] makefile: adjust KBUILD_CFLAGS to reflect kernel.spec for powerpc builds (Josh Poimboeuf) [1578966]
- [redhat] configs: enable CONFIG_LIVEPATCH (Josh Poimboeuf) [1578966]
- [kernel] livepatch: Allow to call a custom callback when freeing shadow variables (Josh Poimboeuf) [1578966]
- [kernel] livepatch: Initialize shadow variables safely by a custom callback (Josh Poimboeuf) [1578966]
- [kernel] livepatch: Small shadow variable documentation fixes (Josh Poimboeuf) [1578966]
- [kernel] livepatch: add locking to force and signal functions (Josh Poimboeuf) [1578966]
- [kernel] livepatch: Remove immediate feature (Josh Poimboeuf) [1578966]
- [kernel] livepatch: force transition to finish (Josh Poimboeuf) [1578966]
- [kernel] livepatch: send a fake signal to all blocking tasks (Josh Poimboeuf) [1578966]
- [kernel] livepatch: __klp_disable_patch() should never be called for disabled patches (Josh Poimboeuf) [1578966]
- [kernel] livepatch: Correctly call klp_post_unpatch_callback() in error paths (Josh Poimboeuf) [1578966]
- [kernel] livepatch: add transition notices (Josh Poimboeuf) [1578966]
- [kernel] livepatch: move transition "complete" notice into klp_complete_transition() (Josh Poimboeuf) [1578966]
- [kernel] livepatch: add (un)patch callbacks (Josh Poimboeuf) [1578966]
- [kernel] livepatch: __klp_shadow_get_or_alloc() is local to shadow.c (Josh Poimboeuf) [1578966]
- [kernel] livepatch: introduce shadow variable API (Josh Poimboeuf) [1578966]
- [kernel] powerpc/livepatch: Implement reliable stack tracing for the consistency model (Josh Poimboeuf) [1578966]
- [kernel] powerpc/modules: Improve restore_r2() error message (Josh Poimboeuf) [1578966]
- [kernel] powerpc/modules: Don't try to restore r2 after a sibling call (Josh Poimboeuf) [1578966]
- [kernel] powerpc/modules: Add REL24 relocation support of livepatch symbols (Josh Poimboeuf) [1578966]
- [powerpc] mm/radix: Change pte relax sequence to handle nest MMU hang (Desnes Augusto Nunes do Rosario) [1582537]
- [powerpc] mm: Change function prototype (Desnes Augusto Nunes do Rosario) [1582537]
- [powerpc] mm/radix: Move function from radix.h to pgtable-radix.c (Desnes Augusto Nunes do Rosario) [1582537]
- [powerpc] mm/hugetlb: Update huge_ptep_set_access_flags to call __ptep_set_access_flags directly (Desnes Augusto Nunes do Rosario) [1582537]
- [powerpc] xive: prepare all hcalls to support long busy delays (Steve Best) [1587855]
- [powerpc] xive: shutdown XIVE when kexec or kdump is performed (Steve Best) [1587855]
- [powerpc] xive: fix hcall H_INT_RESET to support long busy delays (Steve Best) [1587855]
- [powerpc] 64/kexec: fix race in kexec when XIVE is shutdown (Steve Best) [1587855]
- [cpuidle] powernv: Fix promotion from snooze if next state disabled (Steve Best) [1586365]
- [cpufreq] powernv: Fix hardlockup due to synchronous smp_call in timer interrupt (Gustavo Duarte) [1574857]

* Fri Jun 08 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-81.el7a]
- [redhat] configs: Enable HiSilicon SAS v3 driver (Zhou Wang) [1509922]
- [scsi] hisi_sas: Remove depends on HAS_DMA in case of platform dependency (Zhou Wang) [1509922]
- [scsi] hisi_sas: add v3 hw MODULE_DEVICE_TABLE() (Zhou Wang) [1509922]
- [scsi] hisi_sas: modify some register config for hip08 (Zhou Wang) [1509922]
- [scsi] hisi_sas: Code cleanup and minor bug fixes (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix return value of hisi_sas_task_prep() (Zhou Wang) [1509922]
- [scsi] hisi_sas: remove unused variable hisi_sas_devices.running_req (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix the issue of setting linkrate register (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix the issue of link rate inconsistency (Zhou Wang) [1509922]
- [scsi] hisi_sas: support the property of signal attenuation for v2 hw (Zhou Wang) [1509922]
- [scsi] libsas: direct call probe and destruct (Zhou Wang) [1509922]
- [scsi] libsas: Use new workqueue to run sas event and disco event (Zhou Wang) [1509922]
- [scsi] libsas: shut down the PHY if events reached the threshold (Zhou Wang) [1509922]
- [scsi] libsas: remove the numbering for each event enum (Zhou Wang) [1509922]
- [scsi] libsas: Use dynamic alloced work to avoid sas event lost (Zhou Wang) [1509922]
- [scsi] libsas: add event to defer list tail instead of head when draining (Zhou Wang) [1509922]
- [scsi] libsas: rename notify_port_event() for consistency (Zhou Wang) [1509922]
- [scsi] libsas: Disable asynchronous aborts for SATA devices (Zhou Wang) [1509922]
- [scsi] libsas: use flush_workqueue to process disco events synchronously (Zhou Wang) [1509922]
- [scsi] libsas: initialize sas_phy status according to response of DISCOVER (Zhou Wang) [1509922]
- [scsi] libsas: fix error when getting phy events (Zhou Wang) [1509922]
- [scsi] libsas: fix memory leak in sas_smp_get_phy_events() (Zhou Wang) [1509922]
- [scsi] libsas: remove private hex2bin() implementation (Zhou Wang) [1509922]
- [scsi] libsas: fix length error in sas_smp_handler() (Zhou Wang) [1509922]
- [scsi] ata: enhance the definition of SET MAX feature field value (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix a bug in hisi_sas_dev_gone() (Zhou Wang) [1509922]
- [scsi] hisi_sas: directly attached disk LED feature for v2 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: make local symbol host_attrs static (Zhou Wang) [1509922]
- [scsi] hisi_sas: Change frame type for SET MAX commands (Zhou Wang) [1509922]
- [scsi] libsas: make the event threshold configurable (Zhou Wang) [1509922]
- [scsi] hisi_sas: add v3 hw suspend and resume (Zhou Wang) [1509922]
- [scsi] hisi_sas: re-add the lldd_port_deformed() (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix SAS_QUEUE_FULL problem while running IO (Zhou Wang) [1509922]
- [scsi] hisi_sas: add internal abort dev in some places (Zhou Wang) [1509922]
- [scsi] hisi_sas: judge result of internal abort (Zhou Wang) [1509922]
- [scsi] hisi_sas: do link reset for some CHL_INT2 ints (Zhou Wang) [1509922]
- [scsi] hisi_sas: use an general way to delay PHY work (Zhou Wang) [1509922]
- [scsi] hisi_sas: add v2 hw port AXI error handling support (Zhou Wang) [1509922]
- [scsi] hisi_sas: improve int_chnl_int_v2_hw() consistency with v3 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: add some print to enhance debugging (Zhou Wang) [1509922]
- [scsi] hisi_sas: add RAS feature for v3 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: change ncq process for v3 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: add an mechanism to do reset work synchronously (Zhou Wang) [1509922]
- [scsi] hisi_sas: modify hisi_sas_dev_gone() for reset (Zhou Wang) [1509922]
- [scsi] hisi_sas: some optimizations of host controller reset (Zhou Wang) [1509922]
- [scsi] hisi_sas: optimise port id refresh function (Zhou Wang) [1509922]
- [scsi] hisi_sas: relocate clearing ITCT and freeing device (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix dma_unmap_sg() parameter (Zhou Wang) [1509922]
- [scsi] hisi_sas: initialize dq spinlock before use (Zhou Wang) [1509922]
- [scsi] sas: Convert timers to use timer_setup() (Zhou Wang) [1509922]
- [scsi] hisi_sas: add v3 hw port AXI error handling (Zhou Wang) [1509922]
- [scsi] hisi_sas: add v3 hw support for AXI fatal error (Zhou Wang) [1509922]
- [scsi] hisi_sas: complete all tasklets prior to host reset (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix a bug when free device for v3 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: add hisi_hba.rst_work init for v3 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: add v3 hw DFX feature (Zhou Wang) [1509922]
- [scsi] hisi_sas: init connect cfg register for v3 hw (Zhou Wang) [1509922]
- [scsi] hisi_sas: check PHY state in get_wideport_bitmap_v3_hw() (Zhou Wang) [1509922]
- [scsi] hisi_sas: use array for v2 hw AXI errors (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix the risk of freeing slot twice (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix NULL check in SMP abort task path (Zhou Wang) [1509922]
- [scsi] hisi_sas: us start_phy in PHY_FUNC_LINK_RESET (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix SATA breakpoint memory size (Zhou Wang) [1509922]
- [scsi] hisi_sas: grab hisi_hba.lock when processing slots (Zhou Wang) [1509922]
- [scsi] hisi_sas: use spin_lock_irqsave() for hisi_hba.lock (Zhou Wang) [1509922]
- [scsi] hisi_sas: fix internal abort slot timeout bug (Zhou Wang) [1509922]
- [scsi] hisi_sas: delete get_ncq_tag_v3_hw() (Zhou Wang) [1509922]
- [scsi] libsas: remove unused variable sas_ha (Zhou Wang) [1509922]
- [scsi] libsas: kill useless ha_event and do some cleanup (Zhou Wang) [1509922]

* Wed Jun 06 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-80.el7a]
- [fs] dcache: fix quadratic behavior with parallel shrinkers (Miklos Szeredi) [1565210]
- [acpi] numa: parse all entries of SRAT memory affinity table (Zhou Wang) [1575857]
- [acpi] aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1585531]
- [s390] zcrypt: Support up to 256 crypto adapters (Hendrik Brueckner) [1571121]
- [arm64] aarch64: support meltdown/spectre status in sysfs (Mark Salter) [1555408]
- [crypto] pcrypt - fix freeing pcrypt instances (Herbert Xu) [1546458] {CVE-2017-18075}
- [crypto] hmac - require that the underlying hash algorithm is unkeyed (Herbert Xu) [1544462] {CVE-2017-17806}
- [crypto] salsa20 - fix blkcipher_walk API usage (Herbert Xu) [1543982] {CVE-2017-17805}
- [netdrv] sfc: stop the TX queue before pushing new buffers (Jarod Wilson) [1447178]
- [netdrv] cxgb4: copy the length of cpl_tx_pkt_core to fw_wr (Arjun Vynipadath) [1581074]
- [netdrv] cxgb4: avoid schedule while atomic (Arjun Vynipadath) [1581074]
- [netdrv] cxgb4: enable inner header checksum calculation (Arjun Vynipadath) [1581074]
- [netdrv] cxgb4: Fix {vxlan/geneve}_port initialization (Arjun Vynipadath) [1581074]

* Tue Jun 05 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-79.el7a]
- [powerpc] powernv/cpuidle: Init all present cpus for deep states (Steve Best) [1585598]
- [netdrv] ibmvnic: Only do H_EOI for mobility events (Steve Best) [1583094]
- [netdrv] ibmvnic: Fix partial success login retries (Steve Best) [1583094]
- [netdrv] ibmvnic: Introduce hard reset recovery (Steve Best) [1583094]
- [netdrv] ibmvnic: Set resetting state at earliest possible point (Steve Best) [1583094]
- [netdrv] ibmvnic: Create separate initialization routine for resets (Steve Best) [1583094]
- [netdrv] ibmvnic: Handle error case when setting link state (Steve Best) [1583094]
- [netdrv] ibmvnic: Return error code if init interrupted by transport event (Steve Best) [1583094]
- [netdrv] ibmvnic: Check CRQ command return codes (Steve Best) [1583094]
- [netdrv] ibmvnic: Introduce active CRQ state (Steve Best) [1583094]
- [netdrv] ibmvnic: Mark NAPI flag as disabled when released (Steve Best) [1583094]
- [char] tpm: fix race condition in tpm_common_write() (Jerry Snitselaar) [1584495]
- [net] team: move dev_mc_sync after master_upper_dev_link in team_port_add (Xin Long) [1561421]
- [net] team: Fix double free in error path (Xin Long) [1561421]
- [net] team: fall back to hash if table entry is empty (Xin Long) [1561421]
- [net] sctp: do not pr_err for the duplicated node in transport rhlist (Xin Long) [1555193]
- [net] sctp: fix dst refcnt leak in sctp_v4_get_dst (Xin Long) [1555193]
- [net] sctp: fix dst refcnt leak in sctp_v6_get_dst() (Xin Long) [1555193]
- [net] sctp: do not allow the v4 socket to bind a v4mapped v6 address (Xin Long) [1555193]
- [net] sctp: return error if the asoc has been peeled off in sctp_wait_for_sndbuf (Xin Long) [1555193]
- [net] sctp: reinit stream if stream outcnt has been change by sinit in sendmsg (Xin Long) [1555193]
- [net] sctp: add SCTP_CID_RECONF conversion in sctp_cname (Xin Long) [1555193]
- [net] sctp: make sure stream nums can match optlen in sctp_setsockopt_reset_streams (Xin Long) [1555193]
- [net] sctp: do not abandon the other frags in unsent outq if one msg has outstanding frags (Xin Long) [1555193]
- [net] sctp: abandon the whole msg if one part of a fragmented message is abandoned (Xin Long) [1555193]
- [net] sctp: only update outstanding_bytes for transmitted queue when doing prsctp_prune (Xin Long) [1555193]
- [net] sctp: set sender next_tsn for the old result with ctsn_ack_point plus 1 (Xin Long) [1555193]
- [net] sctp: avoid flushing unsent queue when doing asoc reset (Xin Long) [1555193]
- [net] sctp: only allow the asoc reset when the asoc outq is empty (Xin Long) [1555193]
- [net] sctp: only allow the out stream reset when the stream outq is empty (Xin Long) [1555193]
- [net] sctp: set frag_point in sctp_setsockopt_maxseg correctly (Xin Long) [1555193]
- [net] sctp: Always set scope_id in sctp_inet6_skb_msgname (Xin Long) [1555193]
- [net] sctp: check stream reset info len before making reconf chunk (Xin Long) [1555193]
- [net] sctp: use the right sk after waking up from wait_buf sleep (Xin Long) [1555193]
- [net] sctp: do not free asoc when it is already dead in sctp_sendmsg (Xin Long) [1555193]
- [net] sctp: silence warns on sctp_stream_init allocations (Xin Long) [1555193]
- [net] ipv6: fix access to non-linear packet in ndisc_fill_redirect_hdr_option() (Lorenzo Bianconi) [1540005]

* Thu May 31 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-78.el7a]
- [netdrv] cxgb4: Support firmware rdma write completion work request (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Support firmware rdma write with immediate work request (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add support to query HW SRQ parameters (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add support to initialise/read SRQ entries (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Adds CPL support for Shared Receive Queues (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: notify fatal error to uld drivers (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: copy vlan_id in ndo_get_vf_config (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: add support for ndo_set_vf_vlan (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add support for Inline IPSec Tx (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add support for ethtool i2c dump (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: fix error return code in adap_init0() (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: fix missing break in switch and indent return statements (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: support new ISSI flash parts (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: depend on firmware event for link status (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Setup FW queues before registering netdev (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Fix queue free path of ULD drivers (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: check fw caps to set link mode mask (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: do not display 50Gbps as unsupported speed (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: increase max tx rate limit to 100 Gbps (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: do not set needs_free_netdev for mgmt dev's (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: copy adap index to PF0-3 adapter instances (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add TP Congestion map entry for single-port (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: remove dead code when allocating filter (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Extend T3 PCI quirk to T4+ devices (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: free up resources of pf 0-3 (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Fix error handling path in 'init_one()' (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: avoid memcpy beyond end of source buffer (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: IPv6 filter takes 2 tids (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: restructure VF mgmt code (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Fix FW flash errors (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Check alignment constraint for T6 (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: use CLIP with LIP6 on T6 for TCAM filters (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: support for XLAUI Port Type (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: display VNI correctly (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: add new T5 and T6 device id's (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Report tid start range correctly for T6 (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Simplify PCIe Completion Timeout setting (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add support for new flash parts (Arjun Vynipadath) [1526347]
- [netdrv] cxgb4: Add HMA support (Arjun Vynipadath) [1526354 1526347]
- [netdrv] cxgb4: add geneve offload support for T6 (Arjun Vynipadath) [1529695 1526347]
- [netdrv] cxgb4: implement ndo_features_check (Arjun Vynipadath) [1529695 1526347]
- [netdrv] cxgb4: add support for vxlan segmentation offload (Arjun Vynipadath) [1529695 1526347]
- [netdrv] cxgb4: implement udp tunnel callbacks (Arjun Vynipadath) [1529695 1526347]
- [netdrv] cxgb4: add data structures to support vxlan (Arjun Vynipadath) [1529695 1526347]
- [netdrv] cxgb4: speed up on-chip memory read (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: rework on-chip memory read (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: fix trailing zero in CIM LA dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: use backdoor access to collect dumps when firmware crashed (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: fix incorrect condition for using firmware LDST commands (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: reset FW_OK flag on firmware crash (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: properly initialize variables (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: enable ZLIB_DEFLATE when building cxgb4 (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: use zlib deflate to compress firmware dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: update dump collection logic to use compression (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect TX rate limit info in UP CIM logs (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect PCIe configuration logs (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect egress and ingress SGE queue contexts (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: skip TX and RX payload regions in memory dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect HMA memory dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: RSS table is 4k for T6 (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect MC memory dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect on-chip memory information (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect vpd info directly from hardware (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect SGE queue context dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect LE-TCAM dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect hardware misc dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect hardware scheduler dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect PBT tables dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect MPS-TCAM dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect TID info dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect RSS dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect CIM queue configuration dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect hardware LA dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: fix overflow in collecting IBQ and OBQ dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect IBQ and OBQ dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect hardware module dumps (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect TP dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: update API for TP indirect register access (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect firmware mbox and device log dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect on-chip memory dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: collect register dump (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: implement ethtool dump data operations (Arjun Vynipadath) [1526353 1526347]
- [netdrv] cxgb4: make symbol pedits static (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: fix endianness for vlan value in cxgb4_tc_flower (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: set filter type to 1 for ETH_P_IPV6 (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: fix error return code in cxgb4_set_hash_filter() (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add support to create hash-filters via tc-flower offload (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb*: Convert timers to use timer_setup() (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add support to retrieve stats for hash filters (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add support to delete hash filter (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add support to create hash filters (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: initialize hash-filter configuration (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: save additional filter tuple field shifts in tp_params (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower support for L3/L4 rewrite (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: introduce fw_filter2_wr to prepare for L3/L4 rewrite support (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower support for ETH-SMAC rewrite (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: introduce SMT ops to prepare for SMAC rewrite support (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower support for ETH-DMAC rewrite (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower support for action PASS (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower match support for vlan (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower match support for TOS (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: make function ch_flower_stats_cb, fixes warning (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: fetch stats for offloaded tc flower flows (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add support to offload action vlan (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add basic tc flower offload support (Arjun Vynipadath) [1526355 1526347]
- [netdrv] cxgb4: add tc flower offload skeleton (Arjun Vynipadath) [1526355 1526347]

* Thu May 31 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-77.el7a]
- [netdrv] mlx5e: Sync netdev vxlan ports at open (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Avoid using the ipv6 stub in the TC offload neigh update path (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix memory usage issues in offloading TC flows (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix traffic being dropped on VF representor (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Verify coalescing parameters in range (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Make eswitch support to depend on switchdev (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Use 32 bits to store VF representor SQ number (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Don't override vport admin link state in switchdev mode (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Don't clean uninitialized UMR resources (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Fix cleanup order on unload (Alaa Hleihel) [1572092]
- [netdrv] rdma/mlx5: Fix crash while accessing garbage pointer and freed memory (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Fix integer overflows in mlx5_ib_create_srq (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Fix out-of-bounds read in create_raw_packet_qp_rq (Alaa Hleihel) [1572092]
- [netdrv] rdma/mlx5: Fix integer overflow while resizing CQ (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Fix an error code in __mlx5_ib_modify_qp() (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: When not in dual port RoCE mode, use provided port as native (Alaa Hleihel) [1572092]
- [netdrv] {net, ib}/mlx5: Raise fatal IB event when sys error occurs (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Avoid passing an invalid QP type to firmware (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Fix incorrect size of klms in the memory region (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix error handling when adding flow rules (Alaa Hleihel) [1572092]
- [netdrv] mlx5: E-Switch, Fix drop counters use before creation (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Add header re-write to the checks for conflicting actions (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Use 128B cacheline size for 128B or larger cachelines (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Specify numa node when allocating drop rq (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Return error if prio is specified when offloading eswitch vlan push (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Address static checker warnings on non-constant initializers (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Verify inline header size do not exceed SKB linear size (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix loopback self test when GRO is off (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix TCP checksum in LRO buffers (Alaa Hleihel) [1572092]
- [netdrv] mlx5: increase async EQ to avoid EQ overrun (Alaa Hleihel) [1572092]
- [netdrv] mlx5: fix mlx5_get_vector_affinity to start from completion vector 0 (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Fix copy-paste bug in flow steering refactoring (Alaa Hleihel) [1572092]
- [netdrv] rdma/mlx5: Avoid memory leak in case of XRCD dealloc failure (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add likely to the common RX checksum flow (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Extend the stats group API to have update_stats() (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Merge per priority stats groups (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add per-channel counters infrastructure, use it upon TX timeout (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Poll event queue upon TX timeout before performing full channels recovery (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add Event Queue meta data info for TX timeout logs (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Print delta since last transmit per SQ upon TX timeout (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Set hairpin queue size (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Enable setting hairpin queue size (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add RSS support for hairpin (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Vectorize the low level core hairpin object (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Enlarge the NIC TC offload steering prio to support two levels (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Refactor RSS related objects and code (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Set per priority hairpin pairs (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Use vhca id as the hairpin peer identifier (Alaa Hleihel) [1572092]
- [netdrv] rdma/mlx5: Remove redundant allocation warning print (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix trailing semicolon (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Mmap the HCA's clock info to user-space (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add clock info page to mlx5 core devices (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: remove redundant assignment of mdev (Alaa Hleihel) [1572092]
- [netdrv] dim: Fix int overflow (Alaa Hleihel) [1572092]
- [netdrv] dim: use struct net_dim_sample as arg to net_dim (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Move dynamic interrupt coalescing code to linux (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Change Mellanox references in DIM code (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Move generic functions to new file (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Move AM logic enums (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Remove rq references in mlx5e_rx_am (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Move interrupt moderation forward declarations (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Move interrupt moderation structs to new file (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Remove redundant checks in set_ringparam (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: E-switch, Add steering drop counters (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Fix spelling mistake "functionts" -> "functions" (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Add ethtool support to get child time stamping parameters (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Add PTP ioctl support for child interface (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Use correct timestamp in child receive flow (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Support offloading TC NIC hairpin flows (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Basic setup of hairpin object (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Hairpin pair core object setup (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Add hairpin definitions to the FW API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Replace WARN_ONCE with netdev_WARN_ONCE (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Set num_vhca_ports capability (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Don't advertise RAW QP support in dual port mode (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Route MADs for dual port RoCE (Alaa Hleihel) [1572092]
- [netdrv] {net, ib}/mlx5: Change set_roce_gid to take a port number (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Update counter implementation for dual port RoCE (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Change debugfs to have per port contents (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Implement dual port functionality in query routines (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Move IB event processing onto a workqueue (Alaa Hleihel) [1572092]
- [netdrv] {net, ib}/mlx5: Manage port association for multiport RoCE (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Make netdev notifications multiport capable (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Reduce the use of num_port capability (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Set software owner ID during init HCA (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix race for multiple RoCE enable (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add support for DC target QP (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add support for DC Initiator QP (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Handle type IB_QPT_DRIVER when creating a QP (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Enable DC transport (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Add DCT command interface (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Move locks initialization to the corresponding stage (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Move loopback initialization to the corresponding stage (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Move hardware counters initialization to the corresponding stage (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Move ODP initialization to the corresponding stage (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Move RoCE/ETH initialization to the corresponding stage (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Create profile infrastructure to add and remove stages (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Separate ingress/egress namespaces for each vport (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix ingress/egress naming mistake (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: E-Switch, Use the name of static array instead of its address (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Enable QP creation with a given blue flame index (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Expose dynamic mmap allocation (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Extend UAR stuff to support dynamic allocation (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Report inner RSS capability (Alaa Hleihel) [1572092]
- [netdrv] mlx5: E-Switch, Create a dedicated send to vport rule deletion function (Alaa Hleihel) [1572092]
- [netdrv] mlx5: E-Switch, Move mlx5e only logic outside E-Switch (Alaa Hleihel) [1572092]
- [netdrv] mlx5: E-Switch, Refactor load/unload of representors (Alaa Hleihel) [1572092]
- [netdrv] mlx5: E-Switch, Refactor vport representors initialization (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: revisit -Wmaybe-uninitialized warning (Alaa Hleihel) [1572092]
- [netdrv] rdma/mlx5: Fix out-of-bound access while querying AH (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Remove timestamp set from netdevice open flow (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Update ptp_clock_event foreach PPS event (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Don't override netdev features field unless in error flow (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Check support before TC swap in ETS init (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add error print in ETS init (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Keep updating ethtool statistics when the interface is down (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix error handling in load one (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix mlx5_get_uars_page to return error code (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix memory leak in bad flow of mlx5_alloc_irq_vectors (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix get vector affinity helper function (Alaa Hleihel) [1572092]
- [netdrv] {net, ib}/mlx5: Don't disable local loopback multicast traffic when needed (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix steering memory leak (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix misspelling in the error message and comment (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix defaulting RX ring size when not needed (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Fix features check of IPv6 traffic (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Fix rate limit packet pacing naming and struct (Alaa Hleihel) [1572092]
- [netdrv] revert "mlx5: move affinity hints assignments to generic code" (Alaa Hleihel) [1572092]
- [netdrv] mlx5: FPGA, return -EINVAL if size is zero (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add CQ moderation capability to query_device (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Exposing modify CQ callback to uverbs layer (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Fix ABI alignment to 64 bit (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add PCI write end padding support (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: CHECKSUM_COMPLETE offload for VLAN/QinQ packets (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add VLAN offloads statistics (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add 802.1ad VLAN insertion support (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add 802.1ad VLAN filter steering rules (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Declare bitmap using kernel macro (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add rollback on add VLAN failure (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Rename VLAN related variables and functions (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Enable CQE based moderation on TX CQ (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Add inner TTC table to IPoIB flow steering (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Initialize destination_flow struct to 0 (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Enlarge the NIC TC offload table size (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: DCBNL, Add debug messages log (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add support for ethtool msglvl support (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Support DSCP trust state to Ethernet's IP packet on SQ (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Add dcbnl dscp to priority support (Alaa Hleihel) [1572092]
- [netdrv] mlx5: QPTS and QPDPM register firmware command support (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Add MLX5_SET16 and MLX5_GET16 (Alaa Hleihel) [1572092]
- [netdrv] mlx5: QCAM register firmware command support (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch channels counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch ipsec counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch pme counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch per prio pfc counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch per prio traffic counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch pcie counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch ethernet extended counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch physical statistical counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch RFC 2819 counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch RFC 2863 counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch IEEE 802.3 counters to use stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch vport counters to use the stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Switch Q counters to use the stats group API (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: Introduce stats group API (Alaa Hleihel) [1572092]
- [netdrv] mellanox: Convert timers to use timer_setup() (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add support for RSS on the inner packet (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add tunneling offloads support (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Update tunnel offloads bits (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Support padded 128B CQE feature (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Support 128B CQE compression feature (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Add 128B CQE compression and padding HW bits (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Allow creation of a multi-packet RQ (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Expose multi-packet RQ capabilities (Alaa Hleihel) [1572092]
- [netdrv] mlx5: convert fs_node.refcount from atomic_t to refcount_t (Alaa Hleihel) [1572092]
- [netdrv] mlx5: convert mlx5_cq.refcount from atomic_t to refcount_t (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Use ARRAY_SIZE (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Remove a set-but-not-used variable (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5: Suppress gcc 7 fall-through complaints (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Modify rdma netdev allocate and free to support PKEY (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Add PKEY child interface ethtool ops (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Add PKEY child interface ndos (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Add PKEY child interface nic profile (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Use hash-table to map between QPN to child netdev (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Support for setting PKEY index to underlay QP (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Support for attaching multiple underlay QPs to root flow table (Alaa Hleihel) [1572092]
- [netdrv] mlx5e: IPoIB, Move underlay QP init/uninit to separate functions (Alaa Hleihel) [1572092]
- [netdrv] mlx5: PTP code migration to driver core section (Alaa Hleihel) [1572092]
- [netdrv] mlx5: File renaming towards ptp core implementation (Alaa Hleihel) [1572092]
- [netdrv] ib/mlx5:: pr_err() and mlx5_ib_dbg() strings should end with newlines (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Add FGs and FTEs memory pool (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Allocate FTE object without lock (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Support multiple updates of steering rules in parallel (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Replace fs_node mutex with reader/writer semaphore (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Refactor FTE and FG creation code (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Export building of matched flow groups list (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Move the entry index allocator to flow group (Alaa Hleihel) [1572092]
- [netdrv] mlx5: Remove redundant unlikely() (Alaa Hleihel) [1572092]
- [netdrv] mlx5: use setup_timer() helper (Alaa Hleihel) [1572092]

* Thu May 31 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-76.el7a]
- [net] core: Add drop counters to VF statistics (Ivan Vecera) [1574475]
- [net] dcb: Add dscp to priority selector type (Ivan Vecera) [1574475]
- [net] No line break on netdev_WARN* formatting (Ivan Vecera) [1573232]
- [net] Fix netdev_WARN_ONCE macro (Ivan Vecera) [1573232]
- [net] Introduce netdev_*_once functions (Ivan Vecera) [1573232]
- [net] sched: introduce helper to identify gact pass action (Ivan Vecera) [1572458]
- [misc] cxl: Report the tunneled operations status (Steve Best) [1583635]
- [misc] cxl: Set the PBCQ Tunnel BAR register when enabling capi mode (Steve Best) [1583635]
- [scsi] csiostor: remove redundant assignment to pointer 'ln' (Arjun Vynipadath) [1526361]
- [scsi] csiostor: fix spelling mistake: "Couldnt" -> "Couldn't" (Arjun Vynipadath) [1526361]
- [scsi] csiostor: remove unneeded DRIVER_LICENSE #define (Arjun Vynipadath) [1526361]
- [scsi] csiostor: Convert timers to use timer_setup() (Arjun Vynipadath) [1526361]
- [iommu] amd: Take into account that alloc_dev_data() may return NULL (Jerry Snitselaar) [1583787]
- [iommu] vt-d: Don't register bus-notifier under dmar_global_lock (Jerry Snitselaar) [1583787]
- [iommu] vt-d: Fix scatterlist offset handling (Jerry Snitselaar) [1583787]
- [iommu] vt-d: Clear Page Request Overflow fault bit (Jerry Snitselaar) [1583787]
- [tools] perf vendor events arm64: add HiSilicon hip08 JSON file (Xiaojun Tan) [1575880]
- [tools] perf vendor events arm64: fixup A53 to use recommended events (Xiaojun Tan) [1575880]
- [tools] perf vendor events arm64: Fixup ThunderX2 to use recommended events (Xiaojun Tan) [1575880]
- [tools] perf vendor events arm64: Add armv8-recommended.json (Xiaojun Tan) [1575880]
- [tools] perf vendor events: Add support for arch standard events (Xiaojun Tan) [1575880]
- [tools] perf vendor events arm64: Relocate Cortex A53 JSONs to arm subdirectory (Xiaojun Tan) [1575880]
- [tools] perf vendor events arm64: Relocate ThunderX2 JSON to cavium subdirectory (Xiaojun Tan) [1575880]
- [tools] perf vendor events: Add support for pmu events vendor subdirectory (Xiaojun Tan) [1575880]
- [tools] perf vendor events: Drop support for unused topic directories (Xiaojun Tan) [1575880]
- [tools] perf vendor events: Fix error code in json_events() (Xiaojun Tan) [1575880]
- [tools] perf vendor events: Drop incomplete multiple mapfile support (Xiaojun Tan) [1575880]
- [tools] perf vendor events aarch64: Add JSON metrics for ARM Cortex-A53 Processor (Xiaojun Tan) [1575880]
- [tools] perf vendor events arm64: Add ThunderX2 implementation defined pmu core events (Xiaojun Tan) [1575880]
- [tools] perf vendor events: Support metric_group and no event name in JSON parser (Xiaojun Tan) [1575880]
- [tools] perf pmu: Add check for valid cpuid in perf_pmu__find_map() (Xiaojun Tan) [1575880]
- [tools] perf tools arm64: Add support for get_cpuid_str function (Xiaojun Tan) [1575880]
- [tools] perf pmu: Pass pmu as a parameter to get_cpuid_str() (Xiaojun Tan) [1575880]
- [tools] perf list: Add metric groups to perf list (Xiaojun Tan) [1575880]
- [tools] perf stat: Support JSON metrics in perf stat (Xiaojun Tan) [1575880]
- [tools] perf stat: Factor out generic metric printing (Xiaojun Tan) [1575880]
- [powerpc] perf: Fix memory allocation for core-imc based on num_possible_cpus() (Steve Best) [1577973]
- [powerpc] 64s: Add support for a store forwarding barrier at kernel entry/exit (Mauricio Oliveira) [1566913] {CVE-2018-3639}
- [security] ima: re-initialize iint->atomic_flags (Gustavo Duarte) [1560743]
- [security] ima: re-introduce own integrity cache lock (Gustavo Duarte) [1560743]

* Wed May 30 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-75.el7a]
- [netdrv] rhmaintainers: add maintainer for hns driver (Xiaojun Tan) [1509860]
- [netdrv] config: aarch64: enable hns3 network driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix length overflow when CONFIG_ARM64_64K_PAGES (Xiaojun Tan) [1509860]
- [netdrv] hns3: remove unnecessary pci_set_drvdata() and devm_kfree() (Xiaojun Tan) [1509860]
- [netdrv] hns3: never send command queue message to IMP when reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for not initializing VF rss_hash_key problem (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for the wrong shift problem in hns3_set_txbd_baseinfo (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for returning wrong value problem in hns3_get_rss_indir_size (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for returning wrong value problem in hns3_get_rss_key_size (Xiaojun Tan) [1509860]
- [netdrv] hns3: hclge_inform_reset_assert_to_vf() can be static (Xiaojun Tan) [1509860]
- [netdrv] hns3: Changes required in PF mailbox to support VF reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add *Asserting Reset* mailbox message & handling in VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: Changes to support ARQ(Asynchronous Receive Queue) (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support to re-initialize the hclge device (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support to reset the enet/ring mgmt layer (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support to request VF Reset to PF (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add VF Reset device state and its handling (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add VF Reset Service Task to support event handling (Xiaojun Tan) [1509860]
- [netdrv] hns3: Changes to make enet watchdog timeout func common for PF/VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for not returning problem in get_link_ksettings when phy exists (Xiaojun Tan) [1509860]
- [netdrv] hns3: add querying speed and duplex support to VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: add get_link support to VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for getting wrong link mode problem (Xiaojun Tan) [1509860]
- [netdrv] hns3: change the time interval of int_gl calculating (Xiaojun Tan) [1509860]
- [netdrv] hns3: change GL update rate (Xiaojun Tan) [1509860]
- [netdrv] hns3: increase the max time for IMP handle command (Xiaojun Tan) [1509860]
- [netdrv] hns3: export pci table of hclge and hclgevf to userspace (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for vlan table lost problem when resetting (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the VF queue reset flow error (Xiaojun Tan) [1509860]
- [netdrv] hns3: reallocate tx/rx buffer after changing mtu (Xiaojun Tan) [1509860]
- [netdrv] hns3: add result checking for VF when modify unicast mac address (Xiaojun Tan) [1509860]
- [netdrv] hns3: add existence checking before adding unicast mac address (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix return value error of hclge_get_mac_vlan_cmd_status() (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix error type definition of return value (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for buffer overflow smatch warning (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for loopback failure when vlan filter is enable (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for querying pfc puase packets statistic (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix rx path skb->truesize reporting bug (Xiaojun Tan) [1509860]
- [netdrv] hns3: unify the pause params setup function (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for ipv6 address loss problem after setting channels (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for netdev not running problem after calling net_stop and net_open (Xiaojun Tan) [1509860]
- [netdrv] hns3: add existence check when remove old uc mac address (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for coal configuation lost when setting the channel (Xiaojun Tan) [1509860]
- [netdrv] hns3: refactor the coalesce related struct (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for coalesce configuration lost during reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: refactor the get/put_vector function (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for use-after-free when setting ring parameter (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for pause configuration lost during reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for RSS configuration loss problem during reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: refactor the hclge_get/set_rss_tuple function (Xiaojun Tan) [1509860]
- [netdrv] hns3: refactor the hclge_get/set_rss function (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for VF driver inner interface hclgevf_ops.get_tqps_and_rss_info (Xiaojun Tan) [1509860]
- [netdrv] hns3: set the max ring num when alloc netdev (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the queue id for tqp enable&&reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix endian issue when PF get mbx message flag (Xiaojun Tan) [1509860]
- [netdrv] hns3: set the cmdq out_vld bit to 0 after used (Xiaojun Tan) [1509860]
- [netdrv] hns3: VF should get the real rss_size instead of rss_size_max (Xiaojun Tan) [1509860]
- [netdrv] hns3: add int_gl_idx setup for VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: add get/set_coalesce support to VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: converting spaces into tabs to avoid checkpatch.pl warning (Xiaojun Tan) [1509860]
- [netdrv] hns3: add net status led support for fiber port (Xiaojun Tan) [1509860]
- [netdrv] hns3: add ethtool -p support for fiber port (Xiaojun Tan) [1509860]
- [netdrv] hns3: add manager table initialization for hardware (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for get_regs (Xiaojun Tan) [1509860]
- [netdrv] hns3: check for NULL function pointer in hns3_nic_set_features (Xiaojun Tan) [1509860]
- [netdrv] hns3: add feature check when feature changed (Xiaojun Tan) [1509860]
- [netdrv] hns3: add int_gl_idx setup for TX and RX queues (Xiaojun Tan) [1509860]
- [netdrv] hns3: change the unit of GL value macro (Xiaojun Tan) [1509860]
- [netdrv] hns3: remove unused GL setup function (Xiaojun Tan) [1509860]
- [netdrv] hns3: refactor GL update function (Xiaojun Tan) [1509860]
- [netdrv] hns3: refactor interrupt coalescing init function (Xiaojun Tan) [1509860]
- [netdrv] hns3: add ethtool_ops.set_coalesce support to PF (Xiaojun Tan) [1509860]
- [netdrv] hns3: add ethtool_ops.get_coalesce support to PF (Xiaojun Tan) [1509860]
- [netdrv] hns3: remove TSO config command from VF driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: add ethtool_ops.get_channels support for VF (Xiaojun Tan) [1509860]
- [netdrv] hns3: report the function type the same line with hns3_nic_get_stats64 (Xiaojun Tan) [1509860]
- [netdrv] revert "net: hns3: Add packet statistics of netdev" (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add more packet size statisctics (Xiaojun Tan) [1509860]
- [netdrv] hns3: remove redundant semicolon (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for not setting pause parameters (Xiaojun Tan) [1509860]
- [netdrv] hns3: add MTU initialization for hardware (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for changing MTU (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for setting MTU (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for updating fc_mode_last_time (Xiaojun Tan) [1509860]
- [netdrv] hns3: Fix a response data read error of tqp statistics query (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add packet statistics of netdev (Xiaojun Tan) [1509860]
- [netdrv] hns3: Remove a useless member of struct hns3_stats (Xiaojun Tan) [1509860]
- [netdrv] hns3: Fix an error macro definition of HNS3_TQP_STAT (Xiaojun Tan) [1509860]
- [netdrv] hns3: Fix a loop index error of tqp statistics query (Xiaojun Tan) [1509860]
- [netdrv] hns3: Fix an error of total drop packet statistics (Xiaojun Tan) [1509860]
- [netdrv] hns3: Mask the packet statistics query when NIC is down (Xiaojun Tan) [1509860]
- [netdrv] hns3: Modify the update period of packet statistics (Xiaojun Tan) [1509860]
- [netdrv] hns3: Remove repeat statistic of rx_errors (Xiaojun Tan) [1509860]
- [netdrv] hns3: Fix spelling errors (Xiaojun Tan) [1509860]
- [netdrv] hns3: Unify the strings display of packet statistics (Xiaojun Tan) [1509860]
- [netdrv] hns3: Disable VFs change rxvlan offload status (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add ethtool interface for vlan filter (Xiaojun Tan) [1509860]
- [netdrv] hns3: hns3_get_channels() can be static (Xiaojun Tan) [1509860]
- [netdrv] hns3: change TM sched mode to TC-based mode when SRIOV enabled (Xiaojun Tan) [1509860]
- [netdrv] hns3: Increase the default depth of bucket for TM shaper (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for querying advertised pause frame by ethtool ethx (Xiaojun Tan) [1509860]
- [netdrv] hns3: add Asym Pause support to phy default features (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support to update flow control settings after autoneg (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for set_pauseparam (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for getting auto-negotiation state in hclge_get_autoneg (Xiaojun Tan) [1509860]
- [netdrv] hns3: cleanup mac auto-negotiation state query (Xiaojun Tan) [1509860]
- [netdrv] hns3: add handling vlan tag offload in bd (Xiaojun Tan) [1509860]
- [netdrv] hns3: add ethtool related offload command (Xiaojun Tan) [1509860]
- [netdrv] hns3: add vlan offload config command (Xiaojun Tan) [1509860]
- [netdrv] hns3: add a mask initialization for mac_vlan table (Xiaojun Tan) [1509860]
- [netdrv] hns3: get rss_size_max from configuration but not hardcode (Xiaojun Tan) [1509860]
- [netdrv] hns3: free the ring_data structrue when change tqps (Xiaojun Tan) [1509860]
- [netdrv] hns3: change the returned tqp number by ethtool -x (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support to modify tqps number (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support to query tqps number (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add mailbox interrupt handling to PF driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Change PF to add ring-vect binding & resetQ to mailbox (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add mailbox support to PF driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Unified HNS3 {VF|PF} Ethernet Driver for hip08 SoC (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add HNS3 VF driver to kernel build framework (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add HNS3 VF HCL(Hardware Compatibility Layer) Support (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add mailbox support to VF driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add HNS3 VF IMP(Integrated Management Proc) cmd interface (Xiaojun Tan) [1509860]
- [netdrv] hns3: Refactors the requested reset & pending reset handling code (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add reset service task for handling reset requests (Xiaojun Tan) [1509860]
- [netdrv] hns3: Refactor of the reset interrupt handling logic (Xiaojun Tan) [1509860]
- [netdrv] hns3: Updates MSI/MSI-X alloc/free APIs(depricated) to new APIs (Xiaojun Tan) [1509860]
- [netdrv] hns3: cleanup mac auto-negotiation state query in hclge_update_speed_duplex (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix a bug when getting phy address from NCL_config file (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix a bug for phy supported feature initialization (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for nway_reset (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for set_link_ksettings (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix a bug in hns3_driv_to_eth_caps (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for getting advertised_caps in hns3_get_link_ksettings (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix for getting autoneg in hns3_get_link_ksettings (Xiaojun Tan) [1509860]
- [netdrv] hns3: hns3:fix a bug about statistic counter in reset process (Xiaojun Tan) [1509860]
- [netdrv] hns3: Fix a misuse to devm_free_irq (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add reset interface implementation in client (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add timeout process in hns3_enet (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add reset process in hclge_main (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support for misc interrupt (Xiaojun Tan) [1509860]
- [netdrv] hns3: Refactor the initialization of command queue (Xiaojun Tan) [1509860]
- [netdrv] hns3: Refactor mac_init function (Xiaojun Tan) [1509860]
- [netdrv] hns3: Refactor the mapping of tqp to vport (Xiaojun Tan) [1509860]
- [netdrv] hns3: remove a couple of redundant assignments (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the bug when reuse command description in hclge_add_mac_vlan_tbl (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix a bug in hclge_uninit_client_instance (Xiaojun Tan) [1509860]
- [netdrv] hns3: add nic_client check when initialize roce base information (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the bug of hns3_set_txbd_baseinfo (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix a bug about hns3_clean_tx_ring (Xiaojun Tan) [1509860]
- [netdrv] hns3: remove redundant memset when alloc buffer (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the TX/RX ring.queue_index in hns3_ring_get_cfg (Xiaojun Tan) [1509860]
- [netdrv] hns3: get vf count by pci_sriov_get_totalvfs (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the ops check in hns3_get_rxnfc (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the bug when map buffer fail (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix a bug when alloc new buffer (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add mac loopback selftest support in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Refactor the skb receiving and transmitting function (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add mqprio hardware offload support in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns: Convert timers to use timer_setup() (Xiaojun Tan) [1509860]
- [netdrv] hns3: make local functions static (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix the ring count for ETHTOOL_GRXRINGS (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for ETHTOOL_GRXFH (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for set_rxnfc (Xiaojun Tan) [1509860]
- [netdrv] hns3: add support for set_ringparam (Xiaojun Tan) [1509860]
- [netdrv] hns3: fixes the ring index in hns3_fini_ring (Xiaojun Tan) [1509860]
- [netdrv] hns3: Cleanup for non-static function in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Cleanup for endian issue in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Cleanup for struct that used to send cmd to firmware (Xiaojun Tan) [1509860]
- [netdrv] hns3: Consistently using GENMASK in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add hns3_get_handle macro in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: Cleanup for shifting true in hns3 driver (Xiaojun Tan) [1509860]
- [netdrv] hns3: fix null pointer dereference before null check (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add DCB support when interacting with network stack (Xiaojun Tan) [1509860]
- [netdrv] hns3: Setting for fc_mode and dcb enable flag in TM module (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add dcb netlink interface for the support of DCB feature (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add hclge_dcb module for the support of DCB feature (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add some interface for the support of DCB feature (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add tc-based TM support for sriov enabled port (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support for port shaper setting in TM module (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support for PFC setting in TM module (Xiaojun Tan) [1509860]
- [netdrv] hns3: Add support for dynamically buffer reallocation (Xiaojun Tan) [1509860]
- [netdrv] hns3: Support for dynamically assigning tx buffer to TC (Xiaojun Tan) [1509860]
- [netdrv] mqprio: fix potential null pointer dereference on opt (Xiaojun Tan) [1509860]
- [netdrv] mqprio: Introduce new hardware offload mode and shaper in mqprio (Xiaojun Tan) [1509860]

* Fri May 25 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-74.el7a]
- [redhat] configs: CONFIG_HW_RANDOM_TPM is now a bool (Jerry Snitselaar) [1579491]
- [char] tpm_tis: verify locality released before returning from release_locality (Jerry Snitselaar) [1579491]
- [char] tpm: fix intermittent failure with self tests (Jerry Snitselaar) [1579491]
- [char] tpm: add retry logic (Jerry Snitselaar) [1579491]
- [char] tpm: self test failure should not cause suspend to fail (Jerry Snitselaar) [1579491]
- [char] tpm2: add longer timeouts for creation commands (Jerry Snitselaar) [1579491]
- [char] tpm_crb: use __le64 annotated variable for response buffer address (Jerry Snitselaar) [1579491]
- [char] tpm: fix buffer type in tpm_transmit_cmd (Jerry Snitselaar) [1579491]
- [char] tpm: tpm-interface: fix tpm_transmit/_cmd kdoc (Jerry Snitselaar) [1579491]
- [char] tpm: cmd_ready command can be issued only after granting locality (Jerry Snitselaar) [1579491]
- [char] tpm: fix potential buffer overruns caused by bit glitches on the bus (Jerry Snitselaar) [1579491]
- [char] tpm: st33zp24: fix potential buffer overruns caused by bit glitches on the bus (Jerry Snitselaar) [1579491]
- [char] tpm_i2c_infineon: fix potential buffer overruns caused by bit glitches on the bus (Jerry Snitselaar) [1579491]
- [char] tpm_i2c_nuvoton: fix potential buffer overruns caused by bit glitches on the bus (Jerry Snitselaar) [1579491]
- [char] tpm_tis: fix potential buffer overruns caused by bit glitches on the bus (Jerry Snitselaar) [1579491]
- [char] tpm: remove unused variables (Jerry Snitselaar) [1579491]
- [char] tpm: remove unused data fields from I2C and OF device ID tables (Jerry Snitselaar) [1579491]
- [char] tpm: only attempt to disable the LPC CLKRUN if is already enabled (Jerry Snitselaar) [1579491]
- [char] tpm: follow coding style for variable declaration in tpm_tis_core_init() (Jerry Snitselaar) [1579491]
- [char] tpm: delete the TPM_TIS_CLK_ENABLE flag (Jerry Snitselaar) [1579491]
- [char] tpm: Keep CLKRUN enabled throughout the duration of transmit_cmd() (Jerry Snitselaar) [1579491]
- [char] tpm_tis: Move ilb_base_addr to tpm_tis_data (Jerry Snitselaar) [1579491]
- [char] tpm2-cmd: allow more attempts for selftest execution (Jerry Snitselaar) [1579491]
- [char] tpm: return a TPM_RC_COMMAND_CODE response if command is not implemented (Jerry Snitselaar) [1579491]
- [char] tpm: Move Linux RNG connection to hwrng (Jerry Snitselaar) [1579491]
- [char] tpm: use struct tpm_chip for tpm_chip_find_get() (Jerry Snitselaar) [1579491]
- [char] tpm: add event log format version (Jerry Snitselaar) [1579491]
- [char] tpm: rename event log provider files (Jerry Snitselaar) [1579491]
- [char] tpm: move tpm_eventlog.h outside of drivers folder (Jerry Snitselaar) [1579491]
- [char] tpm, tpm_tis: use ARRAY_SIZE() to define TPM_HID_USR_IDX (Jerry Snitselaar) [1579491]
- [char] tpm: fix duplicate inline declaration specifier (Jerry Snitselaar) [1579491]
- [char] tpm: fix type of a local variables in tpm_tis_spi.c (Jerry Snitselaar) [1579491]
- [char] tpm: fix type of a local variable in tpm2_map_command() (Jerry Snitselaar) [1579491]
- [char] tpm: fix type of a local variable in tpm2_get_cc_attrs_tbl() (Jerry Snitselaar) [1579491]
- [char] tpm-dev-common: Reject too short writes (Jerry Snitselaar) [1579491]
- [char] tpm: React correctly to RC_TESTING from TPM 2.0 self tests (Jerry Snitselaar) [1579491]
- [char] tpm: Use dynamic delay to wait for TPM 2.0 self test result (Jerry Snitselaar) [1579491]
- [char] tpm: Trigger only missing TPM 2.0 self tests (Jerry Snitselaar) [1579491]
- [char] tpm_tis_spi: Use DMA-safe memory for SPI transfers (Jerry Snitselaar) [1579491]
- [char] tpm/tpm_crb: Use start method value from ACPI table directly (Jerry Snitselaar) [1579491]
- [char] tpm: constify transmit data pointers (Jerry Snitselaar) [1579491]
- [char] tpm_tis: make array cmd_getticks static const to shrink object code size (Jerry Snitselaar) [1579491]
- [char] tpm: migrate pubek_show to struct tpm_buf (Jerry Snitselaar) [1579491]

* Thu May 24 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-73.el7a]
- [netdrv] mlx4_core: Fix memory leak while delete slave's resources (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Fix mixed PFC and Global pause user control requests (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Include GID type when deleting GIDs from HW table under RoCE (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Fix corruption of RoCEv2 IPv4 GIDs (Erez Alfasi) [1572095]
- [netdrv] ib/mlx: Set slid to zero in Ethernet completion struct (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Fix incorrectly releasing steerable UD QPs when have only ETH ports (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Align behavior of set ring size flow via ethtool (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Add support to RSS hash for inner headers (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Change default QoS settings (Erez Alfasi) [1572095]
- [netdrv] mlx4_core: Cleanup FMR unmapping flow (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: RX csum, reorder branches (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: RX csum, remove redundant branches and checks (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Remove unused ibpd parameter (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Potential buffer overflow in _mlx4_set_path() (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Fix mlx4_ib_alloc_mr error flow (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Fill all counters under one call of stats lock (Erez Alfasi) [1572095]
- [netdrv] mlx4_core: Fix wrong calculation of free counters (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Fix selftest for small MTUs (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Add CQ moderation capability to query_device (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Exposing modify CQ callback to uverbs layer (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Increase maximal message size under UD QP (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Add contig support for control objects (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Use optimal numbers of MTT entries (Erez Alfasi) [1572095]
- [netdrv] mlx4: Use Kconfig flag to remove support of old gen2 Mellanox devices (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Fix RSS's QPC attributes assignments (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Add report for RSS capabilities by vendor channel (Erez Alfasi) [1572095]
- [netdrv] mlx4: convert mlx4_srq.refcount from atomic_t to refcount_t (Erez Alfasi) [1572095]
- [netdrv] mlx4: convert mlx4_qp.refcount from atomic_t to refcount_t (Erez Alfasi) [1572095]
- [netdrv] mlx4: convert mlx4_cq.refcount from atomic_t to refcount_t (Erez Alfasi) [1572095]
- [netdrv] ib/mlx4: Suppress gcc 7 fall-through complaints (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: XDP_TX, assign constant values of TX descs on ring creaion (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Obsolete call to generic write_desc in XDP xmit flow (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Replace netdev parameter with priv in XDP xmit function (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Increase number of default RX rings (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Limit the number of RX rings (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Limit the number of TX rings (Erez Alfasi) [1572095]
- [netdrv] mlx4_en: Use __force to fix a sparse warning in TX datapath (Erez Alfasi) [1572095]
- [netdrv] mlx4_core: Fix cast warning in fw.c (Erez Alfasi) [1572095]
- [netdrv] mlx4: Fix endianness issue in qp context params (Erez Alfasi) [1572095]
- [netdrv] mlx4_core: Convert timers to use timer_setup() (Erez Alfasi) [1572095]

* Thu May 24 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-72.el7a]
- [s390] s390/sthyi: add s390_sthyi system call (Hendrik Brueckner) [1576511]
- [s390] s390/sthyi: add cache to store hypervisor info (Hendrik Brueckner) [1576511]
- [s390] s390/sthyi: reorganize sthyi implementation (Hendrik Brueckner) [1576511]
- [netdrv] ibmvnic: Fix statistics buffers memory leak (Steve Best) [1581605]
- [netdrv] ibmvnic: Fix non-fatal firmware error reset (Steve Best) [1581605]
- [netdrv] ibmvnic: Free coherent DMA memory if FW map failed (Steve Best) [1581605]
- [acpi] iort: Remove temporary iort_get_id_mapping_index() ACPICA guard (Xiaojun Tan) [1510992]
- [acpi] acpica: iasl: Add SMMUv3 device ID mapping index support (Xiaojun Tan) [1510992]
- [acpi] iort: Enable SMMUv3/PMCG IORT MSI domain set-up (Xiaojun Tan) [1510992]
- [acpi] iort: Add SMMUv3 specific special index mapping handling (Xiaojun Tan) [1510992]
- [acpi] iort: Enable special index ITS group mappings for IORT nodes (Xiaojun Tan) [1510992]
- [acpi] iort: Look up IORT node through struct fwnode_handle pointer (Xiaojun Tan) [1510992]
- [acpi] iort: Make platform devices initialization code SMMU agnostic (Xiaojun Tan) [1510992]
- [acpi] iort: Improve functions return type/storage class specifier indentation (Xiaojun Tan) [1510992]
- [acpi] iort: Remove leftover ACPI_IORT_SMMU_V3_PXM_VALID guard (Xiaojun Tan) [1510992]
- [acpi] arm64: pr_err() strings should end with newlines (Xiaojun Tan) [1510992]
- [redhat] config: aarch64: enable Hisilicon LPC driver (Xiaojun Tan) [1266324]
- [bus] hisi lpc: Add Kconfig MFD_CORE dependency (Xiaojun Tan) [1266324]
- [maintainers] maintainers: Add John Garry as maintainer for HiSilicon LPC driver (Xiaojun Tan) [1266324]
- [bus] hisi lpc: Add ACPI support (Xiaojun Tan) [1266324]
- [acpi] acpi / scan: Do not enumerate Indirect IO host children (Xiaojun Tan) [1266324]
- [acpi] acpi / scan: Rename acpi_is_serial_bus_slave() for more general use (Xiaojun Tan) [1266324]
- [bus] hisi lpc: Support the LPC host on Hip06/Hip07 with DT bindings (Xiaojun Tan) [1266324]
- [of] Add missing I/O range exception for indirect-IO devices (Xiaojun Tan) [1266324]
- [kernel] pci: Apply the new generic I/O management on PCI IO hosts (Xiaojun Tan) [1266324]
- [kernel] pci: Add fwnode handler as input param of pci_register_io_range() (Xiaojun Tan) [1266324]
- [pci] Remove __weak tag from pci_register_io_range() (Xiaojun Tan) [1266324]
- [lib] Add generic PIO mapping method (Xiaojun Tan) [1266324]
- [acpi] acpi / scan: Fix enumeration for special UART devices (Xiaojun Tan) [1266324]

* Thu May 24 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-71.el7a]
- [mm] ksm: fix inconsistent accounting of zero pages (Mauricio Oliveira) [1567111]
- [scsi] ipr: new IOASC update (Steve Best) [1520409]
- [powerpc] mce: Fix a bug where mce loops on memory UE (Desnes Augusto Nunes do Rosario) [1571178]
- [netdrv] hinic: add pci device ids for 25ge and 100ge card (Zhou Wang) [1577077]
- [powerpc] pseries: Enable RAS hotplug events later (Sam Bobroff) [1535304]
- [arm64] mm: fix thinko in non-global page table attribute check (Mark Langsdorf) [1575146] {CVE-2017-5715}
- [arm64] Move BP hardening to check_and_switch_context (Mark Langsdorf) [1575146] {CVE-2017-5715}
- [arm64] Run enable method for errata work arounds on late CPUs (Mark Langsdorf) [1575146] {CVE-2017-5715}
- [redhat] config: arm64: enable some ras features (Xiaojun Tan) [1570238]
- [arm64] kvm: arm64: Emulate RAS error registers and set HCR_EL2's TERR & TEA (Xiaojun Tan) [1570238]
- [arm64] kvm: arm64: Handle RAS SErrors from EL2 on guest exit (Xiaojun Tan) [1570238]
- [virt] kvm: arm64: Handle RAS SErrors from EL1 on guest exit (Xiaojun Tan) [1570238]
- [arm64] kvm: arm64: Save ESR_EL2 on guest SError (Xiaojun Tan) [1570238]
- [arm64] kvm: arm64: Save/Restore guest DISR_EL1 (Xiaojun Tan) [1570238]
- [arm64] kvm: arm64: Set an impdef ESR for Virtual-SError using VSESR_EL2 (Xiaojun Tan) [1570238]
- [virt] kvm: arm/arm64: mask/unmask daif around VHE guests (Xiaojun Tan) [1570238]
- [arm64] kernel: Prepare for a DISR user (Xiaojun Tan) [1570238]
- [arm64] Unconditionally enable IESB on exception entry/return for firmware-first (Xiaojun Tan) [1570238]
- [arm64] kernel: Survive corrected RAS errors notified by SError (Xiaojun Tan) [1570238]
- [arm64] cpufeature: Detect CPU RAS Extentions (Xiaojun Tan) [1570238]
- [arm64] sysreg: Move to use definitions for all the SCTLR bits (Xiaojun Tan) [1570238]
- [arm64] cpufeature: __this_cpu_has_cap() shouldn't stop early (Xiaojun Tan) [1575146 1570238] {CVE-2017-5715}
- [kernel] efi: Parse ARM error information value (Xiaojun Tan) [1570238]
- [kernel] efi: Move ARM CPER code to new file (Xiaojun Tan) [1570238]
- [arm64] fault: avoid send SIGBUS two times (Xiaojun Tan) [1570238]
- [arm64] kvm: arm/arm64: fix the incompatible matching for external abort (Xiaojun Tan) [1570238]
- [arm64] entry.s: move SError handling into a C function for future expansion (Xiaojun Tan) [1570238]
- [acpi] acpi / apei: Convert timers to use timer_setup() (Xiaojun Tan) [1570238]
- [arm64] mm: don't write garbage into TTBR1_EL1 register (Robert Richter) [1575146 1575138] {CVE-2017-5715}
- [cpufreq] cppc: Use transition_delay_us depending transition_latency (Robert Richter) [1510199]
- [cpufreq] cppc_cpufreq: Fix cppc_cpufreq_init() failure path (Robert Richter) [1510199]
- [acpi] acpi / cppc: Use 64-bit arithmetic instead of 32-bit (Robert Richter) [1510199]
- [acpi] cppc: remove initial assignment of pcc_ss_data (Robert Richter) [1510199]
- [acpi] acpi / cppc: Fix KASAN global out of bounds warning (Robert Richter) [1510199]
- [acpi] acpi / cppc: Make CPPC ACPI driver aware of PCC subspace IDs (Robert Richter) [1510199]
- [acpi] mailbox: pcc: Move the MAX_PCC_SUBSPACES definition to header file (Robert Richter) [1510199]
- [i2c] ipmi_ssif: Fix kernel panic at msg_done_handler (Robert Richter) [1555339]
- [i2c] xlp9xx: Handle NACK on DATA properly (Robert Richter) [1555339]
- [i2c] xlp9xx: Check for Bus state before every transfer (Robert Richter) [1555339]
- [i2c] revert "xlp9xx: Check for Bus state after every transfer" (Robert Richter) [1555339]

* Wed May 23 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-70.el7a]
- [kernel] genirq/affinity: Spread irq vectors among present CPUs as far as possible (Ming Lei) [1550547]
- [kernel] genirq/affinity: Allow irq spreading from a given starting point (Ming Lei) [1550547]
- [kernel] genirq/affinity: Move actual irq vector spreading into a helper function (Ming Lei) [1550547]
- [kernel] genirq/affinity: Rename *node_to_possible_cpumask as *node_to_cpumask (Ming Lei) [1550547]
- [kernel] genirq/affinity: Don't return with empty affinity masks on error (Ming Lei) [1550547]
- [scsi] virtio_scsi: unify scsi_host_template (Ming Lei) [1550547]
- [scsi] virtio_scsi: fix IO hang caused by automatic irq vector affinity (Ming Lei) [1550547]
- [scsi] core: introduce force_blk_mq (Ming Lei) [1550547]
- [scsi] megaraid_sas: fix selection of reply queue (Ming Lei) [1550547]
- [scsi] hpsa: fix selection of reply queue (Ming Lei) [1550547]
- [block] blk-mq: don't check queue mapped in __blk_mq_delay_run_hw_queue() (Ming Lei) [1550547]
- [kernel] blk-mq: remove blk_mq_delay_queue() (Ming Lei) [1550547]
- [block] blk-mq: introduce blk_mq_hw_queue_first_cpu() to figure out first cpu (Ming Lei) [1550547]
- [block] blk-mq: avoid to write intermediate result to hctx->next_cpu (Ming Lei) [1550547]
- [block] blk-mq: don't keep offline CPUs mapped to hctx 0 (Ming Lei) [1550547]
- [block] blk-mq: make sure that correct hctx->next_cpu is set (Ming Lei) [1550547]
- [block] blk-mq: turn WARN_ON in __blk_mq_run_hw_queue into printk (Ming Lei) [1550547]
- [block] blk-mq: make sure hctx->next_cpu is set correctly (Ming Lei) [1550547]
- [block] blk-mq: simplify queue mapping & schedule with each possisble CPU (Ming Lei) [1550547]
- [kernel] genirq/affinity: assign vectors to all possible CPUs (Ming Lei) [1550547]

* Tue May 22 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-69.el7a]
- [scsi] qla2xxx: Update driver version to 10.00.00.06.07.6a-k (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Correct setting of SAM_STAT_CHECK_CONDITION (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: correctly shift host byte (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix race condition between iocb timeout and initialisation (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Avoid double completion of abort command (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix small memory leak in qla2x00_probe_one on probe failure (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: fix error message on <qla2400 (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix Async GPN_FT for FCP and FC-NVMe scan (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix retry for PRLI RJT with reason of BUSY (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix n2n_ae flag to prevent dev_loss on PDB change (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Set IIDMA and fcport state before qla_nvme_register_remote() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Remove unneeded message and minor cleanup for FC-NVMe (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Restore ZIO threshold setting (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: fix spelling mistake: "existant" -> "existent" (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use dma_pool_zalloc() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix function argument descriptions (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Remove unused symbols (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use p for printing pointers (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Remove FC_NO_LOOP_ID for FCP and FC-NVMe Discovery (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix crashes in qla2x00_probe_one on probe failure (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix FC-NVMe LUN discovery (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: ensure async flags are reset correctly (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: do not check login_state if no loop id is assigned (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fixup locking for session deletion (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix NULL pointer crash due to active timer for ABTS (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix incorrect handle for abort IOCB (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix double free bug after firmware timeout (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix a locking imbalance in qlt_24xx_handle_els() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Avoid triggering undefined behavior in qla2x00_mbx_completion() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add XCB counters to debugfs (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix queue ID for async abort with Multiqueue (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix warning for code intentation in __qla24xx_handle_gpdb_event() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix warning during port_name debug print (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix warning in qla2x00_async_iocb_timeout() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix recursion while sending terminate exchange (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: remove redundant assignment of d (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use zeroing allocator rather than allocator/memset (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Serialize session free in qlt_free_session_done (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Serialize session deletion by using work_lock (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Remove unused argument from qlt_schedule_sess_for_deletion() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Prevent relogin trigger from sending too many commands (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Prevent multiple active discovery commands per session (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add retry limit for fabric scan logic (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Delay loop id allocation at login (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Increase verbosity of debug messages logged (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Allow relogin and session creation after reset (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add ability to use GPNFT/GNNFT for RSCN handling (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Properly extract ADISC error codes (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix GPNFT/GNNFT error handling (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Remove session creation redundant code (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Migrate switch registration commands away from mailbox interface (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix login state machine freeze (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Reduce trace noise for Async Events (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Reduce the use of terminate exchange (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add lock protection around host lookup (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add switch command to simplify fabric discovery (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use known NPort ID for Management Server login (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix session cleanup for N2N (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Tweak resource count dump (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Allow target mode to accept PRLI in dual mode (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Don't call dma_free_coherent with IRQ disabled (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add ability to send PRLO (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add option for use reserve exch for ELS (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use shadow register for ISP27XX (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Enable ATIO interrupt handshake for ISP27XX (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Move work element processing out of DPC thread (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Replace GPDB with async ADISC command (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix Firmware dump size for Extended login and Exchange Offload (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Chip reset uses wrong lock during IO flush (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add boundary checks for exchanges to be offloaded (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use chip reset to bring down laser on unload (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use IOCB path to submit Control VP MBX command (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix NULL pointer access for fcport structure (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix smatch warning in qla25xx_delete_{rsp|req}_que (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: remove duplicate includes (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Suppress gcc 7 fall-through warnings (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix memory leak in dual/target mode (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix system crash in qlt_plogi_ack_unref (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Remove aborting ELS IOCB call issued as part of timeout (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Clear loop id after delete (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix scan state field for fcport (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Replace fcport alloc with qla2x00_alloc_fcport (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix abort command deadlock due to spinlock (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix PRLI state check (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix Relogin being triggered too fast (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Relogin to target port on a cable swap (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix NPIV host cleanup in target mode (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix login state machine stuck at GPDB (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Serialize GPNID for multiple RSCN (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Retry switch command on time out (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix re-login for Nport Handle in use (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Skip IRQ affinity for Target QPairs (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Move session delete to driver work queue (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix gpnid error processing (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Fix system crash for Notify ack timeout handling (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Suppress a kernel complaint in qla_init_base_qpair() (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: don't break the bsg-lib abstractions (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Query FC4 type during RSCN processing (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Use ql2xnvmeenable to enable Q-Pair for FC-NVMe (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Changes to support N2N logins (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Allow MBC_GET_PORT_DATABASE to query and save the port states (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Add ATIO-Q processing for INTx mode (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Reinstate module parameter ql2xenablemsix (Himanshu Madhani) [1520458]
- [scsi] qla2xxx: Cocci spatch "pool_zalloc-simple" (Himanshu Madhani) [1520458]

* Mon May 21 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-68.el7a]
- [powerpc] mm/hash64: Zero PGD pages on allocation (Mauricio Oliveira) [1523831]
- [powerpc] mm/hash64: Store the slot information at the right offset for hugetlb (Mauricio Oliveira) [1523831]
- [powerpc] mm/hash64: Allocate larger PMD table if hugetlb config is enabled (Mauricio Oliveira) [1523831]
- [powerpc] mm: Fix crashes with 16G huge pages (Mauricio Oliveira) [1523831]
- [powerpc] sys_pkey_mprotect() system call (Mauricio Oliveira) [1523831]
- [powerpc] sys_pkey_alloc() and sys_pkey_free() system calls (Mauricio Oliveira) [1523831]
- [powerpc] Enable pkey subsystem (Mauricio Oliveira) [1523831]
- [powerpc] ptrace: Add memory protection key regset (Mauricio Oliveira) [1523831]
- [powerpc] Deliver SEGV signal on pkey violation (Mauricio Oliveira) [1523831]
- [powerpc] introduce get_mm_addr_key() helper (Mauricio Oliveira) [1523831]
- [powerpc] Handle exceptions caused by pkey violation (Mauricio Oliveira) [1523831]
- [powerpc] implementation for arch_vma_access_permitted() (Mauricio Oliveira) [1523831]
- [powerpc] check key protection for user page access (Mauricio Oliveira) [1523831]
- [powerpc] helper to validate key-access permissions of a pte (Mauricio Oliveira) [1523831]
- [powerpc] Program HPTE key protection bits (Mauricio Oliveira) [1523831]
- [powerpc] map vma key-protection bits to pte key bits (Mauricio Oliveira) [1523831]
- [powerpc] implementation for arch_override_mprotect_pkey() (Mauricio Oliveira) [1523831]
- [powerpc] ability to associate pkey to a vma (Mauricio Oliveira) [1523831]
- [powerpc] introduce execute-only pkey (Mauricio Oliveira) [1523831]
- [powerpc] store and restore the pkey state across context switches (Mauricio Oliveira) [1523831]
- [powerpc] ability to create execute-disabled pkeys (Mauricio Oliveira) [1523831]
- [powerpc] implementation for arch_set_user_pkey_access() (Mauricio Oliveira) [1523831]
- [powerpc] cleanup AMR, IAMR when a key is allocated or freed (Mauricio Oliveira) [1523831]
- [powerpc] helper functions to initialize AMR, IAMR and UAMOR registers (Mauricio Oliveira) [1523831]
- [powerpc] helper function to read, write AMR, IAMR, UAMOR registers (Mauricio Oliveira) [1523831]
- [powerpc] track allocation status of all pkeys (Mauricio Oliveira) [1523831]
- [powerpc] initial pkey plumbing (Mauricio Oliveira) [1523831]
- [powerpc] mm: Add proper pte access check helper for other platforms (Mauricio Oliveira) [1523831]
- [powerpc] mm/book3s/64: Add proper pte access check helper (Mauricio Oliveira) [1523831]
- [powerpc] mm/hugetlb: Use pte_access_permitted for hugetlb access check (Mauricio Oliveira) [1523831]
- [powerpc] capture the PTE format changes in the dump pte report (Mauricio Oliveira) [1523831]
- [powerpc] use helper functions to get and set hash slots (Mauricio Oliveira) [1523831]
- [powerpc] Swizzle around 4K PTE bits to free up bit 5 and bit 6 (Mauricio Oliveira) [1523831]
- [powerpc] shifted-by-one hidx value (Mauricio Oliveira) [1523831]
- [powerpc] Free up four 64K PTE bits in 64K backed HPTE pages (Mauricio Oliveira) [1523831]
- [powerpc] Free up four 64K PTE bits in 4K backed HPTE pages (Mauricio Oliveira) [1523831]
- [powerpc] introduce pte_get_hash_gslot() helper (Mauricio Oliveira) [1523831]
- [powerpc] introduce pte_set_hidx() helper (Mauricio Oliveira) [1523831]
- [powerpc] powernv: Add debugfs interface for imc-mode and imc-command (Mauricio Oliveira) [1521130]
- [powerpc] perf: Fix pmu_count to count only nest imc pmus (Mauricio Oliveira) [1521130]

* Wed May 16 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-67.el7a]
- [infiniband] iw_cxgb4: Change error/warn prints to pr_debug (Arjun Vynipadath) [1526351]
- [infiniband] iw_cxgb4: Add ib_device->get_netdev support (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Use structs to describe the uABI instead of opencoding (Arjun Vynipadath) [1526351]
- [infiniband] iw_cxgb4: initialize ib_mr fields for user mrs (Arjun Vynipadath) [1526351]
- [infiniband] iw_cxgb4: print mapped ports correctly (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Add a sanity check in process_work() (Arjun Vynipadath) [1526351]
- [infiniband] iw_cxgb4: make pointer reg_workq static (Arjun Vynipadath) [1526351]
- [infiniband] cxgb4: use ktime_get for timestamps (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Annotate r2 and stag as __be32 (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Declare stag as __be32 (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Convert timers to use timer_setup() (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Remove a set-but-not-used variable (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Suppress gcc 7 fall-through complaints (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Remove the obsolete kernel module option 'c4iw_debug' (Arjun Vynipadath) [1526351]
- [infiniband] rdma/cxgb4: Fix indentation (Arjun Vynipadath) [1526351]

* Tue May 15 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-66.el7a]
- [redhat] rhmaintainerns: update target maintainer (Maurizio Lombardi)
- [redhat] configs: Enable Huawei Intelligent PCIE Network Card (Zhou Wang) [1510700]
- [netdrv] net-next/hinic: add arm64 support (Zhou Wang) [1510700]
- [netdrv] hinic: Replace PCI pool old API (Zhou Wang) [1510700]
- [netdrv] net-next/hinic: Fix a case of Tx Queue is Stopped forever (Zhou Wang) [1510700]
- [netdrv] net-next/hinic: Set Rxq irq to specific cpu for NUMA (Zhou Wang) [1510700]
- [netdrv] ibmvnic: Define vnic_login_client_data name field as unsized array (Steve Best) [1576685]
- [netdrv] ibmvnic: Clean actual number of RX or TX pools (Steve Best) [1576685]
- [netdrv] cxgb4vf: Forcefully link up virtual interfaces (Arjun Vynipadath) [1526350]
- [target] cxgbit: call neigh_event_send() to update MAC address (Arjun Vynipadath) [1526349]
- [crypto] chelsio - don't leak pointers to authenc keys (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Remove declaration of static function from header (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Split Hash requests for large scatter gather list (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Fix iv passed in fallback path for rfc3686 (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Update IV before sending request to HW (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Fix src buffer dma length (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Use kernel round function to align lengths (Arjun Vynipadath) [1526362]
- [crypto] chelsio - no csum offload for ipsec path (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Make function aead_ccm_validate_input static (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Fix indentation warning (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Remove dst sg size zero check (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Add authenc versions of ctr and sha (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Fix IV updated in XTS operation (Arjun Vynipadath) [1526362]
- [crypto] chelsio - check for sg null (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Fix Indentation (Arjun Vynipadath) [1526362]
- [crypto] chelsio - fix a type cast error (Arjun Vynipadath) [1526362]
- [crypto] chelsio - select CRYPTO_GF128MUL (Arjun Vynipadath) [1526362]
- [crypto] chcr: ensure cntrl is initialized to fix bit-wise or'ing of garabage data (Arjun Vynipadath) [1526362]
- [crypto] chcr: remove unused variables net_device, pi, adap and cntrl (Arjun Vynipadath) [1526362]
- [crypto] chelsio - make arrays sgl_ent_len and dsgl_ent_len static (Arjun Vynipadath) [1526362]
- [crypto] chcr: Add support for Inline IPSec (Arjun Vynipadath) [1526362]
- [crypto] chelsio - Fix an error code in chcr_hash_dma_map() (Arjun Vynipadath) [1526362]
- [crypto] chelsio - remove redundant assignments to reqctx and dst_size (Arjun Vynipadath) [1526362]
- [misc] genwqe: Fix a typo in two comments (Steve Best) [1520433]
- [misc] genwqe: Remove unused parameter in some functions (Steve Best) [1520433]
- [misc] genwqe: Make defines uppercase (Steve Best) [1520433]
- [misc] genwqe: Remove unused variable and rename function (Steve Best) [1520433]
- [kernel] kdump: coding style fix for commit b40c5c057 (Lianbo Jiang) [1520728]
- [powerpc] xive: Fix trying to "push" an already active pool VP (Desnes Augusto Nunes do Rosario) [1570016]
- [powerpc] fscr: Enable interrupts earlier before calling get_user() (Desnes Augusto Nunes do Rosario) [1562005]
- [powerpc] revert "powernv: Increase memory block size to 1GB on radix" (Mauricio Oliveira) [1574524]

* Wed May 09 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-65.el7a]
- [scsi] cxgb4i: silence overflow warning in t4_uld_rx_handler() (Arjun Vynipadath) [1526348]
- [scsi] megaraid_sas: driver version 07.702.06.00-rh2 (Tomas Henzl) [1553228]
- [scsi] megaraid_sas: Do not use 32-bit atomic request descriptor for Ventura controllers (Tomas Henzl) [1553228]
- [scsi] mpt3sas: Bump mpt3sas driver version to v15.100.01.00 (Tomas Henzl) [1553228]
- [scsi] mpt3sas: Do not use 32-bit atomic request descriptor for Ventura controllers (Tomas Henzl) [1553228]
- [netdrv] revert "net/mlx5: Add fast unload support in shutdown flow" (Jonathan Toppins) [1573351]
- [netdrv] revert "net/mlx5: Remove the flag MLX5_INTERFACE_STATE_SHUTDOWN" (Jonathan Toppins) [1573351]
- [netdrv] revert "net/mlx5: Cancel health poll before sending panic teardown command" (Jonathan Toppins) [1573351]
- [powerpc] powerpc/powernv/npu: Do a PID GPU TLB flush when invalidating a large address range (Mauricio Oliveira) [1571167]
- [powerpc] powernv/npu: Prevent overwriting of pnv_npu2_init_contex() callback parameters (Mauricio Oliveira) [1568164]
- [powerpc] powernv/npu: Add lock to prevent race in concurrent context init/destroy (Mauricio Oliveira) [1568164]
- [powerpc] powernv/memtrace: Let the arch hotunplug code flush cache (Mauricio Oliveira) [1571156]
- [powerpc] mm: Flush cache on memory hot(un)plug (Mauricio Oliveira) [1571156]
- [powerpc] pseries: Fix cpu hotplug crash with memoryless nodes (Serhii Popovych) [1472728]
- [powerpc] numa: Ensure nodes initialized for hotplug (Serhii Popovych) [1472728]
- [powerpc] numa: Use ibm, max-associativity-domains to discover possible nodes (Serhii Popovych) [1472728]

* Fri May 04 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-64.el7a]
- [scsi] cxlflash: Handle spurious interrupts (Steve Best) [1520410]
- [scsi] cxlflash: Remove commmands from pending list on timeout (Steve Best) [1520410]
- [scsi] cxlflash: Synchronize reset and remove ops (Steve Best) [1520410]
- [scsi] cxlflash: Enable OCXL operations (Steve Best) [1520410]
- [scsi] cxlflash: Support AFU reset (Steve Best) [1520410]
- [scsi] cxlflash: Register for translation errors (Steve Best) [1520410]
- [scsi] cxlflash: Introduce OCXL context state machine (Steve Best) [1520410]
- [scsi] cxlflash: Update synchronous interrupt status bits (Steve Best) [1520410]
- [scsi] cxlflash: Setup LISNs for master contexts (Steve Best) [1520410]
- [scsi] cxlflash: Setup LISNs for user contexts (Steve Best) [1520410]
- [scsi] cxlflash: Introduce object handle fop (Steve Best) [1520410]
- [scsi] cxlflash: Support file descriptor mapping (Steve Best) [1520410]
- [scsi] cxlflash: Support adapter context mmap and release (Steve Best) [1520410]
- [scsi] cxlflash: Support adapter context reading (Steve Best) [1520410]
- [scsi] cxlflash: Support adapter context polling (Steve Best) [1520410]
- [scsi] cxlflash: Support starting user contexts (Steve Best) [1520410]
- [scsi] cxlflash: Support AFU interrupt mapping and registration (Steve Best) [1520410]
- [scsi] cxlflash: Support AFU interrupt management (Steve Best) [1520410]
- [scsi] cxlflash: Support process element lifecycle (Steve Best) [1520410]
- [scsi] cxlflash: Setup OCXL transaction layer (Steve Best) [1520410]
- [scsi] cxlflash: Setup function OCXL link (Steve Best) [1520410]
- [scsi] cxlflash: Support reading adapter VPD data (Steve Best) [1520410]
- [scsi] cxlflash: Support AFU state toggling (Steve Best) [1520410]
- [scsi] cxlflash: Support process specific mappings (Steve Best) [1520410]
- [scsi] cxlflash: Support starting an adapter context (Steve Best) [1520410]
- [scsi] cxlflash: MMIO map the AFU (Steve Best) [1520410]
- [scsi] cxlflash: Support image reload policy modification (Steve Best) [1520410]
- [scsi] cxlflash: Support adapter context discovery (Steve Best) [1520410]
- [scsi] cxlflash: Support adapter file descriptors for OCXL (Steve Best) [1520410]
- [scsi] cxlflash: Use IDR to manage adapter contexts (Steve Best) [1520410]
- [scsi] cxlflash: Adapter context support for OCXL (Steve Best) [1520410]
- [scsi] cxlflash: Setup AFU PASID (Steve Best) [1520410]
- [scsi] cxlflash: Setup AFU acTag range (Steve Best) [1520410]
- [scsi] cxlflash: Read host AFU configuration (Steve Best) [1520410]
- [scsi] cxlflash: Setup function acTag range (Steve Best) [1520410]
- [scsi] cxlflash: Read host function configuration (Steve Best) [1520410]
- [scsi] cxlflash: Hardware AFU for OCXL (Steve Best) [1520410]
- [scsi] cxlflash: Introduce OCXL backend (Steve Best) [1520410]
- [scsi] cxlflash: Add argument identifier names (Steve Best) [1520410]
- [scsi] cxlflash: Avoid clobbering context control register value (Steve Best) [1520410]
- [scsi] cxlflash: Preserve number of interrupts for master contexts (Steve Best) [1520410]
- [scsi] cxlflash: Staging to support future accelerators (Steve Best) [1520410]
- [scsi] cxlflash: Adapter context init can return error (Steve Best) [1520410]
- [scsi] cxlflash: Remove embedded CXL work structures (Steve Best) [1520410]
- [scsi] cxlflash: Explicitly cache number of interrupts per context (Steve Best) [1520410]
- [scsi] cxlflash: Update cxl-specific arguments to generic cookie (Steve Best) [1520410]
- [scsi] cxlflash: Reset command ioasc (Steve Best) [1520410]
- [scsi] cxlflash: get rid of pointless access_ok() (Steve Best) [1520410]

* Fri May 04 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-63.el7a]
- [infiniband] rdma/ucma: Introduce safer rdma_addr_size() variants (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Check that device exists prior to accessing it (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Check that device is connected prior to access it (Jonathan Toppins) [1549977]
- [infiniband] rdma/rdma_cm: Fix use after free race with process_one_req (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Correct option size check using optlen (Jonathan Toppins) [1549977]
- [infiniband] rdma/restrack: Move restrack_clean to be symmetrical to restrack_init (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Ensure that CM_ID exists prior to access it (Jonathan Toppins) [1549977]
- [infiniband] rdma/verbs: Remove restrack entry from XRCD structure (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Fix use-after-free access in ucma_close (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Check AF family prior resolving address (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Don't allow join attempts for unsupported AF family (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Fix access to non-initialized CM_ID object (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Do not use invalid destination in determining port reuse (Jonathan Toppins) [1549977]
- [infiniband] rdmavt: Fix synchronization around percpu_ref (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Check that user doesn't overflow QP state (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Limit possible option size (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix possible crash to access NULL netdev (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Reduce poll batch for direct cq polling (Jonathan Toppins) [1549977]
- [infiniband] ib/core : Add null pointer check in addr_resolve (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix missing RDMA cgroups release in case of failure to register device (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Fix kernel panic while using XRC_TGT QP type (Jonathan Toppins) [1549977]
- [infiniband] rdma/restrack: don't use uaccess_kernel() (Jonathan Toppins) [1549977]
- [infiniband] rdma/verbs: Check existence of function prior to accessing it (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Fix usage of user response structures in ABI file (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Sanitize user entered port numbers prior to access it (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Fix circular locking dependency (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Fix bad unlock balance in ib_uverbs_close_xrcd (Jonathan Toppins) [1549977]
- [infiniband] rdma/restrack: Increment CQ restrack object before committing (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Protect from command mask overflow (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Fix unbalanced unlock on error path for rdma_explicit_destroy (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Improve lockdep_check (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Protect from races between lookup and destroy of uobjects (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Hold the uobj write lock after allocate (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Fix possible oops with duplicate ioctl attributes (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Add ioctl support for 32bit processes (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Use __aligned_u64 for uapi headers (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Fix method merging in uverbs_ioctl_merge (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Use u64_to_user_ptr() not a union (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Use inline data transfer for UHW_IN (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Always use the attribute size provided by the user (Jonathan Toppins) [1549977]
- [infiniband] rdma/restrack: Remove unimplemented XRCD object (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Do not warn if IPoIB debugfs doesn't exist (Jonathan Toppins) [1572097 1549977]
- [infiniband] svcrdma: Fix Read chunk round-up (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Use the standard kConfig format for experimental (Jonathan Toppins) [1549977]
- [infiniband] ib: Update references to libibverbs (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Fix BUG after a device removal (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Fix calculation of ri_max_send_sges (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Avoid a potential OOPs for an unused optional parameter (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Map iWarp AH type to undefined in rdma_ah_find_type (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Fix for potential no-carrier state (Jonathan Toppins) [1572097 1549977]
- [infiniband] rdma/nldev: missing error code in nldev_res_get_doit() (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: remove redudant parameter in rxe_av_fill_ip_info (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: change the function rxe_av_fill_ip_info to void (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: change the function to void from int (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: remove unnecessary parameter in rxe_av_to_attr (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: change the function to void from int (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: remove redudant parameter in function (Jonathan Toppins) [1549977]
- [infiniband] rdma/netlink: Hide unimplemented NLDEV commands (Jonathan Toppins) [1549977]
- [infiniband] rdma/nldev: Provide detailed QP information (Jonathan Toppins) [1549977]
- [infiniband] rdma/nldev: Provide global resource utilization (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Add resource tracking for create and destroy PDs (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Add resource tracking for create and destroy CQs (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Add resource tracking for create and destroy QPs (Jonathan Toppins) [1549977]
- [infiniband] rdma/restrack: Add general infrastructure to track RDMA resources (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Save kernel caller name when creating PD and CQ objects (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Use the MODNAME instead of the function name for pd callers (Jonathan Toppins) [1549977]
- [infiniband] rdma: Move enum ib_cq_creation_flags to uapi headers (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: Change RDMA_RXE kconfig to use select (Jonathan Toppins) [1549977]
- [infiniband] rdma/cm: Fix access to uninitialized variable (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Use existing netif_is_bond_master function (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Avoid SGID attributes query while converting GID from OPA to IB (Jonathan Toppins) [1549977]
- [infiniband] ib/umad: Fix use of unprotected device pointer (Jonathan Toppins) [1549977]
- [infiniband] ib/iser: Combine substrings for three messages (Jonathan Toppins) [1549977]
- [infiniband] ib/iser: Delete an unnecessary variable initialisation in iser_send_data_out() (Jonathan Toppins) [1549977]
- [infiniband] ib/iser: Delete an error message for a failed memory allocation in iser_send_data_out() (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Use an unambiguous errno for method not supported (Jonathan Toppins) [1549977]
- [infiniband] rdma/srpt: Fix RCU debug build error (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Add target_can_queue login parameter (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Add RDMA/CM support (Jonathan Toppins) [1549977]
- [infiniband] kobject: Export kobj_ns_grab_current() and kobj_ns_drop() (Jonathan Toppins) [1549977]
- [infiniband] sunrpc: Trace xprt_timer events (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Correct some documenting comments (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Fix "bytes registered" accounting (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Instrument allocation/release of rpcrdma_req/rep objects (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points to instrument QP and CQ access upcalls (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points in the client-side backchannel code paths (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points for connect events (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points to instrument MR allocation and recovery (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points to instrument memory invalidation (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points in reply decoder path (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points to instrument memory registration (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points in the RPC Reply handler paths (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add trace points in RPC Call transmit paths (Jonathan Toppins) [1549977]
- [infiniband] rpcrdma: infrastructure for static trace points in rpcrdma.ko (Jonathan Toppins) [1549977]
- [infiniband] rdma/ib: Add trace point macros to display human-readable values (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Update RoCE multicast routines to use net namespace (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Update cma_validate_port to honor net namespace (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Refactor to access multiple fields of rdma_dev_addr (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Check existence of netdevice during port validation (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Simplify rdma_addr_get_sgid() to not support RoCE (Jonathan Toppins) [1549977]
- [infiniband] rdma/ucma: Use rdma cm API to query GID (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Introduce API to read GIDs for multiple transports (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Move the code for parsing struct ib_cm_req_event_param (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Preparations for adding RDMA/CM support (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Don't allow reordering of commands on wait list (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Fix a race condition related to wait list processing (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Fix login-related race conditions (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Log all zero-length writes and completions (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Simplify srpt_close_session() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Rework multi-channel support (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Use the source GID as session name (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: One target per port (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Add P_Key support (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Rework srpt_disconnect_ch_sync() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Make it safe to use RCU for srpt_device.rch_list (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Refactor srp_send_req() (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Improve path record query error message (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Use kstrtoull() instead of simple_strtoull() (Jonathan Toppins) [1549977]
- [infiniband] ib/cq: Don't force IB_POLL_DIRECT poll context for ib_process_cq_direct (Jonathan Toppins) [1549977]
- [infiniband] ib/core: postpone WR initialization during queue drain (Jonathan Toppins) [1549977]
- [infiniband] rdma/rxe: Fix rxe_qp_cleanup() (Jonathan Toppins) [1549977]
- [infiniband] rdma/rxe: Fix a race condition in rxe_requester() (Jonathan Toppins) [1549977]
- [infiniband] svcrdma: Post Receives in the Receive completion handler (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Introduce rpcrdma_mw_unmap_and_put (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove usage of "mw" (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Replace all usage of "frmr" with "frwr" (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Don't clear RPC_BC_PA_IN_USE on pre-allocated rpc_rqst's (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Split xprt_rdma_send_request (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: buf_free not called for CB replies (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Move unmap-safe logic to rpcrdma_marshal_req (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Support IPv6 in xprt_rdma_set_port (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove another sockaddr_storage field (cdata::addr) (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Initialize the xprt address string array earlier (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove unused padding variables (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove ri_reminv_expected (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Per-mode handling for Remote Invalidation (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Eliminate unnecessary lock cycle in xprt_rdma_send_request (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Fix backchannel allocation of extra rpcrdma_reps (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Fix buffer leak after transport set up failure (Jonathan Toppins) [1549977]
- [infiniband] ib/cma: use strlcpy() instead of strncpy() (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Clarify rdma_ah_find_type (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix ib_wc structure size to remain in 64 bytes boundary (Jonathan Toppins) [1549977]
- [infiniband] rdma: Mark imm_data as be32 in the verbs uapi header (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Limit DMAC resolution to RoCE Connected QPs (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Attempt DMAC resolution for only RoCE (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Limit DMAC resolution to userspace QPs (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Perform modify QP on real one (Jonathan Toppins) [1549977]
- [infiniband] fix sw/rdmavt/* kernel-doc notation (Jonathan Toppins) [1549977]
- [infiniband] fix core/fmr_pool.c kernel-doc notation (Jonathan Toppins) [1549977]
- [infiniband] fix core/verbs.c kernel-doc notation (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Fix rdma_cm path querying for RoCE (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Fix rdma_cm raw IB path setting for RoCE (Jonathan Toppins) [1549977]
- [infiniband] rdma/{cma, ucma}: Simplify and rename rdma_set_ib_paths (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Provide a function to set RoCE path record L2 parameters (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Use the right net namespace for the rdma_cm_id (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Increase number of char device minors (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Remove the locking for character device bitmaps (Jonathan Toppins) [1549977]
- [infiniband] rdma/rxe: Fix a race condition related to the QP error state (Jonathan Toppins) [1549977]
- [infiniband] iser-target: Fix possible use-after-free in connection establishment error (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: remove unnecessary skb_clone in xmit (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: add the static type to the variable (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Micro-optimize I/O context state manipulation (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Inline srpt_get_cmd_state() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Introduce srpt_format_guid() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Reduce frequency of receive failure messages (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Convert a warning into a debug message (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Use the IPv6 format for GIDs in log messages (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Verify port numbers in srpt_event_handler() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Reduce the severity level of a log message (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Rename a local variable, a member variable and a constant (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Document all structure members in ib_srpt.h (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Fix kernel-doc warnings in ib_srpt.c (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Remove an unused structure member (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Change roce_rescan_device to return void (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Introduce driver QP type (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Add encode/decode FDR/EDR rates (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Fix ACL lookup during login (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Disable RDMA access by the initiator (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix two kernel warnings triggered by rxe registration (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Fix for notify send CQ failure messages (Jonathan Toppins) [1572097 1549977]
- [infiniband] rdma/cma: Mark end of CMA ID messages (Jonathan Toppins) [1549977]
- [infiniband] rdma/netlink: Fix locking around __ib_get_device_by_index (Jonathan Toppins) [1549977]
- [infiniband] rdma/nldev: Refactor setting the nldev handle to a common function (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Replace open-coded variant of put_device (Jonathan Toppins) [1549977]
- [infiniband] rdma/netlink: Simplify code of autoload modules (Jonathan Toppins) [1549977]
- [infiniband] rdma/rxe: Remove useless EXPORT_SYMBOL (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Use zeroing memory allocator than allocator/memset (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Fix race condition in neigh creation (Jonathan Toppins) [1572097 1549977]
- [infiniband] rdma/vmw_pvrdma: Remove usage of BIT() from UAPI header (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Use refcount_t instead of atomic_t (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Use more specific sizeof in kcalloc (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Clarify QP and CQ is_kernel logic (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Add UAR SRQ macros in ABI header file (Jonathan Toppins) [1549977]
- [infiniband] drop unknown function from core_priv.h (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Make sure that PSN does not overflow (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Fix command checking as part of ib_uverbs_ex_modify_qp() (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Use rdma_cap_opa_mad to check for OPA (Jonathan Toppins) [1549977]
- [infiniband] ib/sa: Check dlid before SA agent queries for ClassPortInfo (Jonathan Toppins) [1549977]
- [infiniband] infiniband: remove duplicate includes (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Fix lockdep issue found on ipoib_ib_dev_heavy_flush (Jonathan Toppins) [1572097 1549977]
- [infiniband] rdma/vmw_pvrdma: Avoid use after free due to QP/CQ/SRQ destroy (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Use refcount_dec_and_test to avoid warning (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Call ib_umem_release on destroy QP path (Jonathan Toppins) [1549977]
- [infiniband] ib/cm: Refactor to avoid setting path record software only fields (Jonathan Toppins) [1549977]
- [infiniband] ib/{core, umad, cm}: Rename ib_init_ah_from_wc to ib_init_ah_attr_from_wc (Jonathan Toppins) [1549977]
- [infiniband] ib/{core, cm, cma, ipoib}: Rename ib_init_ah_from_path to ib_init_ah_attr_from_path (Jonathan Toppins) [1549977]
- [infiniband] ib/cm: Fix sleeping while spin lock is held (Jonathan Toppins) [1549977]
- [infiniband] ib/cm: Handle address handle attribute init error (Jonathan Toppins) [1549977]
- [infiniband] ib/{cm, umad}: Handle av init error (Jonathan Toppins) [1549977]
- [infiniband] ib/{core, ipoib}: Simplify ib_find_gid to search only for IB link layer (Jonathan Toppins) [1572097 1549977]
- [infiniband] rdma/core: Avoid copying ifindex twice (Jonathan Toppins) [1549977]
- [infiniband] rdma/{core, cma}: Simplify rdma_translate_ip (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Removed unused function (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Avoid redundant memcpy in rdma_addr_find_l2_eth_by_grh (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Avoid exporting module internal ib_find_gid_by_filter() (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: Avoid passing unused index pointer which is optional (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Refactor to avoid unnecessary check on GID lookup miss (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Avoid unnecessary type cast (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Introduce and use helper functions to init work (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Avoid setting path record type twice (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Simplify netdev check (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Set default GID type as RoCE when resolving RoCE route (Jonathan Toppins) [1549977]
- [infiniband] ib/umem: Fix use of npages/nmap fields (Jonathan Toppins) [1549977]
- [infiniband] ib/cm: Add debug prints to ib_cm (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix memory leak in cm_req_handler error flows (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Use correct size when writing netlink stats (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Update pathrec field if not valid record (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/ipoib: Avoid memory leak if the SA returns a different DGID (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/core: Avoid exporting module internal function (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Depend on IPv6 stack to resolve link local address for RoCEv2 (Jonathan Toppins) [1549977]
- [infiniband] ib/{core/cm}: Fix generating a return AH for RoCEE (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Spread reply processing over more CPUs (Jonathan Toppins) [1549977]
- [infiniband] rdma/iwpm: Fix uninitialized error code in iwpm_send_mapinfo() (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Warn when one port fails to initialize (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/ipoib: Restore MM behavior in case of tx_ring allocation failure (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/srp: replace custom implementation of hex2bin() (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Replace printk with pr_warn (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/core: Use PTR_ERR_OR_ZERO() (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Do not re-calculate npages (Jonathan Toppins) [1549977]
- [infiniband] ib/cm: Change sgid to IB GID when handling CM request (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Init subsys if compiled to vmlinuz-core (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Make sure that PSN is not over max allowed (Jonathan Toppins) [1549977]
- [infiniband] ib: INFINIBAND should depend on HAS_DMA (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Update copyright notices (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove include for linux/prefetch.h (Jonathan Toppins) [1549977]
- [infiniband] rpcrdma: Remove C structure definitions of XDR data items (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Put Send CQ in IB_POLL_WORKQUEUE mode (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove atomic send completion counting (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: RPC completion should wait for Send completion (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Refactor rpcrdma_deferred_completion (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add a field of bit flags to struct rpcrdma_req (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Add data structure to manage RDMA Send arguments (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: "Unoptimize" rpcrdma_prepare_hdr_sge() (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Change return value of rpcrdma_prepare_send_sges() (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Fix error handling in rpcrdma_prepare_msg_sges() (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Clean up SGE accounting in rpcrdma_prepare_msg_sges() (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Decode credits field in rpcrdma_reply_handler (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Invoke rpcrdma_reply_handler directly from RECV completion (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Refactor rpcrdma_reply_handler some more (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Move decoded header fields into rpcrdma_rep (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Throw away reply when version is unrecognized (Jonathan Toppins) [1549977]
- [infiniband] infiniband/sw/rdmavt/qp.c: use kmalloc_array_node() (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Rename kernel modify_cq to better describe its usage (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Add CQ moderation capability to query_device (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: Allow CQ moderation with modify CQ (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: Make function rdma_copy_addr return void (Jonathan Toppins) [1549977]
- [infiniband] rdma/vmw_pvrdma: Add shared receive queue support (Jonathan Toppins) [1549977]
- [infiniband] rdma/core: avoid uninitialized variable warning in create_udata (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Convert OPA AH to IB for Extended LIDs only (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Ensure that modifying the use_srq configfs attribute works (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Wait until channel release has finished during module unload (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Introduce srpt_disconnect_ch_sync() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Introduce helper functions for SRQ allocation and freeing (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Post receive work requests after qp transition to INIT state (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Add PCI write end padding flags for WQ and QP (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: don't crash, if allocation of crc algorithm failed (Jonathan Toppins) [1549977]
- [infiniband] rdma/umem: Avoid partial declaration of non-static function (Jonathan Toppins) [1549977]
- [infiniband] svcrdma: Enqueue after setting XPT_CLOSE in completion handlers (Jonathan Toppins) [1549977]
- [infiniband] svcrdma: Preserve CB send buffer across retransmits (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: Convert timers to use timer_setup() (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Change number of TX wqe to 64 (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/ipoib: Use NAPI in UD/TX flows (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/ipoib: Get rid of the tx_outstanding variable in all modes (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/core: Fix calculation of maximum RoCE MTU (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix unable to change lifespan entry for hw_counters (Jonathan Toppins) [1549977]
- [infiniband] ib: Let ib_core resolve destination mac address (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Introduce and use rdma_create_user_ah (Jonathan Toppins) [1549977]
- [infiniband] ib/rdmavt: Convert timers to use timer_setup() (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Make CM timeout dependent on subnet timeout (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Cache global rkey (Jonathan Toppins) [1549977]
- [infiniband] ib/srp: Remove second argument of srp_destroy_qp() (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Change default behavior from using SRQ to using RC (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Cache global L_Key (Jonathan Toppins) [1549977]
- [infiniband] ib/srpt: Limit the send and receive queue sizes to what the HCA supports (Jonathan Toppins) [1549977]
- [infiniband] rdma/uverbs: Make the code in ib_uverbs_cmd_verbs() less confusing (Jonathan Toppins) [1549977]
- [infiniband] ib/rdmavt: Don't wait for resources in QP reset (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Remove ro_unmap_safe (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Use ro_unmap_sync in xprt_rdma_send_request (Jonathan Toppins) [1549977]
- [infiniband] xprtrdma: Don't defer fencing an async RPC's chunks (Jonathan Toppins) [1549977]
- [infiniband] rdma/rxe: Suppress gcc 7 fall-through complaints (Jonathan Toppins) [1549977]
- [infiniband] rdma/rdmavt: Suppress gcc 7 fall-through complaints (Jonathan Toppins) [1549977]
- [infiniband] rdma/isert: Suppress gcc 7 fall-through complaints (Jonathan Toppins) [1549977]
- [infiniband] rdma/iwcm: Remove a set-but-not-used variable (Jonathan Toppins) [1549977]
- [infiniband] rdma/cma: Avoid triggering undefined behavior (Jonathan Toppins) [1549977]
- [infiniband] ib/cm: Suppress gcc 7 fall-through complaints (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Fix endianness annotation in rdma_is_multicast_addr() (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Add ability to set PKEY index to lower device driver (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/ipoib: Grab rtnl lock on heavy flush when calling ndo_open/stop (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/core: remove redundant check on prot_sg_cnt (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Simplify sa_path_set_[sd]lid() calls (Jonathan Toppins) [1549977]
- [infiniband] add MMU dependency for user_mem (Jonathan Toppins) [1549977]
- [infiniband] ib/ipoib: Convert timers to use timer_setup() (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/rxe: put the pool on allocation failure (Jonathan Toppins) [1549977]
- [infiniband] ib/rxe: check for allocation failure on elem (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Do not warn on lid conversions for OPA (Jonathan Toppins) [1549977]
- [infiniband] ib/rdmavt: Correct issues with read-mostly and send size cache lines (Jonathan Toppins) [1549977]
- [infiniband] ib/core: Use __be32 for LIDs in opa_is_extended_lid (Jonathan Toppins) [1549977]
- [infiniband] ib/{ipoib, iser}: Consistent print format of vendor error (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/ipoib: Remove device when one port fails to init (Jonathan Toppins) [1572097 1549977]
- [infiniband] ib/uverbs: clean up INIT_UDATA() macro usage (Jonathan Toppins) [1549977]
- [infiniband] ib/uverbs: clean up INIT_UDATA_BUF_OR_NULL usage (Jonathan Toppins) [1549977]
- [infiniband] ib: Move PCI dependency from root KConfig to HW's KConfigs (Jonathan Toppins) [1549977]
- [infiniband] ib/core: fix spelling mistake: "aceess" -> "access" (Jonathan Toppins) [1549977]

* Fri May 04 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-62.el7a]
- [redhat] rhmaintainers: update networking (Jiri Benc)
- [redhat] configs: Remove CONFIG_SHARED_KERNEL from the s390x configs (Thomas Huth) [1547639]
- [redhat] configs: Enable CONFIG_DRM_VIRTIO_GPU and CONFIG_INPUT_EVDEV on s390x (Thomas Huth) [1570088]
- [s390] setup: enable display support for KVM guest (Thomas Huth) [1570088]
- [s390] char: Rename EBCDIC keymap variables (Thomas Huth) [1570088]
- [s390] kconfig: Remove HAS_IOMEM dependency for Graphics support (Thomas Huth) [1570088]
- [s390] Enable -Werror on s390x builds (Thomas Huth) [1567091]
- [pci] remove messages about reassigning resources (Desnes Augusto Nunes do Rosario) [1507206]
- [scsi] lpfc: update driver version to 12.0.0.2 (Dick Kennedy) [1567372]
- [scsi] lpfc: Correct missing remoteport registration during link bounces (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix NULL pointer reference when resetting adapter (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix nvme remoteport registration race conditions (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix driver not recovering NVME rports during target link faults (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix WQ/CQ creation for older asic's (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix NULL pointer access in lpfc_nvme_info_show (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix lingering lpfc_wq resource after driver unload (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix Abort request WQ selection (Dick Kennedy) [1567372]
- [scsi] lpfc: Enlarge nvmet asynchronous receive buffer counts (Dick Kennedy) [1567372]
- [scsi] lpfc: Add per io channel NVME IO statistics (Dick Kennedy) [1567372]
- [scsi] lpfc: Correct target queue depth application changes (Dick Kennedy) [1567372]
- [scsi] lpfc: Fix multiple PRLI completion error path (Dick Kennedy) [1567372]
- [scsi] lpfc: make several unions static, fix non-ANSI prototype (Dick Kennedy) [1567372]
- [iommu] revert "aarch64: Set bypass mode per default" (Xiaojun Tan) [1569308]
- [netdrv] tg3: Add Macronix NVRAM support (Jonathan Toppins) [1520416]
- [netdrv] tg3: Enable PHY reset in MTU change path for 5720 (Jonathan Toppins) [1520416]
- [netdrv] tg3: Add workaround to restrict 5762 MRRS to 2048 (Jonathan Toppins) [1520416]
- [netdrv] tg3: Update copyright (Jonathan Toppins) [1520416]
- [netdrv] drivers: net: tg3: use setup_timer() helper (Jonathan Toppins) [1520416]
- [netdrv] qcom: emac: Use proper free methods during TX (Steve Ulrich) [1548469]
- [netdrv] ibmvnic: Clear pending interrupt after device reset (Steve Best) [1568302]
- [powerpc] eeh: Fix enabling bridge MMIO windows (Steve Best) [1570018]

* Fri Apr 20 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-61.el7a]
- [scsi] scsi_transport_fc: fix typos on 64/128 GBit define names (Dick Kennedy) [1533961]
- [scsi] scsi_transport_fc: add 64GBIT and 128GBIT port speed definitions (Dick Kennedy) [1533961]
- [scsi] lpfc: Change Copyright of 12.0.0.1 modified files to 2018 (Dick Kennedy) [1533961]
- [scsi] lpfc: update driver version to 12.0.0.1 (Dick Kennedy) [1533961]
- [scsi] lpfc: Memory allocation error during driver start-up on power8 (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix mailbox wait for POST_SGL mbox command (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix SCSI lun discovery when port configured for both SCSI and NVME (Dick Kennedy) [1533961]
- [scsi] lpfc: Streamline NVME Targe6t WQE setup (Dick Kennedy) [1533961]
- [scsi] lpfc: Streamline NVME Initiator WQE setup (Dick Kennedy) [1533961]
- [scsi] lpfc: Code cleanup for 128byte wqe data type (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix NVME Initiator FirstBurst (Dick Kennedy) [1533961]
- [scsi] lpfc: Add missing unlock in WQ full logic (Dick Kennedy) [1533961]
- [scsi] lpfc: use __raw_writeX on DPP copies (Dick Kennedy) [1533961]
- [scsi] lpfc: Change Copyright of 12.0.0.0 modified files to 2018 (Dick Kennedy) [1533961]
- [scsi] lpfc: update driver version to 12.0.0.0 (Dick Kennedy) [1533961]
- [scsi] lpfc: Work around NVME cmd iu SGL type (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix nvme embedded io length on new hardware (Dick Kennedy) [1533961]
- [scsi] lpfc: Add embedded data pointers for enhanced performance (Dick Kennedy) [1533961]
- [scsi] lpfc: Enable fw download on if_type=6 devices (Dick Kennedy) [1533961]
- [scsi] lpfc: Add if_type=6 support for cycling valid bits (Dick Kennedy) [1533961]
- [scsi] lpfc: Add 64G link speed support (Dick Kennedy) [1533961]
- [scsi] lpfc: Add PCI Ids for if_type=6 hardware (Dick Kennedy) [1533961]
- [scsi] lpfc: Add push-to-adapter support to sli4 (Dick Kennedy) [1533961]
- [scsi] lpfc: Add SLI-4 if_type=6 support to the code base (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix crash after bad bar setup on driver attachment (Dick Kennedy) [1533961]
- [scsi] lpfc: Rework sli4 doorbell infrastructure (Dick Kennedy) [1533961]
- [scsi] lpfc: Rework lpfc to allow different sli4 cq and eq handlers (Dick Kennedy) [1533961]
- [scsi] lpfc: Update 11.4.0.7 modified files for 2018 Copyright (Dick Kennedy) [1533961]
- [scsi] lpfc: update driver version to 11.4.0.7 (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix nonrecovery of NVME controller after cable swap (Dick Kennedy) [1533961]
- [scsi] lpfc: Treat SCSI Write operation Underruns as an error (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix header inclusion in lpfc_nvmet (Dick Kennedy) [1533961]
- [scsi] lpfc: Validate adapter support for SRIU option (Dick Kennedy) [1533961]
- [scsi] lpfc: Indicate CONF support in NVMe PRLI (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix issue_lip if link is disabled (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix soft lockup in lpfc worker thread during LIP testing (Dick Kennedy) [1533961]
- [scsi] lpfc: Allow set of maximum outstanding SCSI cmd limit for a target (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix RQ empty firmware trap (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix IO failure during hba reset testing with nvme io (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix PRLI handling when topology type changes (Dick Kennedy) [1533961]
- [scsi] lpfc: Add WQ Full Logic for NVME Target (Dick Kennedy) [1533961]
- [scsi] lpfc: correct debug counters for abort (Dick Kennedy) [1533961]
- [scsi] lpfc: move placement of target destroy on driver detach (Dick Kennedy) [1533961]
- [scsi] lpfc: Increase CQ and WQ sizes for SCSI (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix frequency of Release WQE CQEs (Dick Kennedy) [1533961]
- [scsi] lpfc: fix a couple of minor indentation issues (Dick Kennedy) [1533961]
- [scsi] lpfc: don't dereference localport before it has been null checked (Dick Kennedy) [1533961]
- [scsi] lpfc: correct sg_seg_cnt attribute min vs default (Dick Kennedy) [1533961]
- [scsi] lpfc: update driver version to 11.4.0.6 (Dick Kennedy) [1533961]
- [scsi] lpfc: Beef up stat counters for debug (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix infinite wait when driver unregisters a remote NVME port (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix issues connecting with nvme initiator (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix SCSI LUN discovery when SCSI and NVME enabled (Dick Kennedy) [1533961]
- [scsi] lpfc: Increase SCSI CQ and WQ sizes (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix receive PRLI handling (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix -EOVERFLOW behavior for NVMET and defer_rcv (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix random heartbeat timeouts during heavy IO (Dick Kennedy) [1533961]
- [scsi] lpfc: update driver version to 11.4.0.5 (Dick Kennedy) [1533961]
- [scsi] lpfc: small sg cnt cleanup (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix driver handling of nvme resources during unload (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix crash during driver unload with running nvme traffic (Dick Kennedy) [1533961]
- [scsi] lpfc: Correct driver deregistrations with host nvme transport (Dick Kennedy) [1533961]
- [scsi] lpfc: correct port registrations with nvme_fc (Dick Kennedy) [1533961]
- [scsi] lpfc: Linux LPFC driver does not process all RSCNs (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix ndlp ref count for pt2pt mode issue RSCN (Dick Kennedy) [1533961]
- [scsi] lpfc: Adjust default value of lpfc_nvmet_mrq (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix display for debugfs queInfo (Dick Kennedy) [1533961]
- [scsi] lpfc: Raise maximum NVME sg list size for 256 elements (Dick Kennedy) [1533961]
- [scsi] lpfc: Fix NVME LS abort_xri (Dick Kennedy) [1533961]
- [scsi] lpfc: Handle XRI_ABORTED_CQE in soft IRQ (Dick Kennedy) [1533961]
- [scsi] lpfc: Expand WQE capability of every NVME hardware queue (Dick Kennedy) [1533961]

* Wed Apr 18 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-60.el7a]
- [arm64] futex: Mask __user pointers prior to dereference (Mark Langsdorf) [1543627]
- [arm64] uaccess: Mask __user pointers for __arch_{clear, copy_*}_user (Mark Langsdorf) [1543627]
- [arm64] uaccess: Don't bother eliding access_ok checks in __{get, put}_user (Mark Langsdorf) [1543627]
- [arm64] uaccess: Prevent speculative use of the current addr_limit (Mark Langsdorf) [1543627]
- [arm64] entry: Ensure branch through syscall table is bounded under speculation (Mark Langsdorf) [1543627]
- [arm64] Use pointer masking to limit uaccess speculation (Mark Langsdorf) [1543627]
- [arm64] Make USER_DS an inclusive limit (Mark Langsdorf) [1543627]
- [arm64] move TASK_* definitions to <asm/processor.h> (Mark Langsdorf) [1543627]
- [arm64] Implement array_index_mask_nospec() (Mark Langsdorf) [1543627]
- [arm64] barrier: Add CSDB macros to control data-value prediction (Mark Langsdorf) [1543627]
- [arm64] idmap: Use awx flags for .idmap.text .pushsection directives (Mark Langsdorf) [1543627]
- [arm64] entry: Reword comment about post_ttbr_update_workaround (Mark Langsdorf) [1543627]
- [arm64] Force KPTI to be disabled on Cavium ThunderX (Mark Langsdorf) [1543627]
- [arm64] kpti: Add ->enable callback to remap swapper using nG mappings (Mark Langsdorf) [1543627]
- [arm64] mm: Permit transitioning from Global to Non-Global without BBM (Mark Langsdorf) [1543627]
- [arm64] kpti: Make use of nG dependent on arm64_kernel_unmapped_at_el0() (Mark Langsdorf) [1543627]

* Wed Apr 18 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-59.el7a]
- [redhat] configs: Enable CONFIG_MPROFILE_KERNEL for powerpc64le (and fix spec template) (Mauricio Oliveira) [1551643]
- [redhat] redhat kconfig: Enable ocxl driver for Open Coherent Accelerator Processor Interface devices (Steve Best) [1396036]
- [uapi] ocxl: Add get_metadata IOCTL to share OCXL information to userspace (Steve Best) [1396036]
- [misc] ocxl: Fix potential bad errno on irq allocation (Steve Best) [1396036]
- [misc] ocxl: fix signed comparison with less than zero (Steve Best) [1396036]
- [maintainers] ocxl: add MAINTAINERS entry (Steve Best) [1396036]
- [documentation] ocxl: Documentation (Steve Best) [1396036]
- [misc] cxl: Remove support for "Processing accelerators" class (Steve Best) [1396036]
- [misc] ocxl: Add Makefile and Kconfig (Steve Best) [1396036]
- [misc] ocxl: Add trace points (Steve Best) [1396036]
- [misc] ocxl: Add a kernel API for other opencapi drivers (Steve Best) [1396036]
- [uapi] ocxl: Add AFU interrupt support (Steve Best) [1396036]
- [uapi] ocxl: Driver code for 'generic' opencapi devices (Steve Best) [1396036]
- [misc] powerpc/powernv: Capture actag information for the device (Steve Best) [1396036]
- [powerpc] powernv: Add platform-specific services for opencapi (Steve Best) [1396036]
- [powerpc] powernv: Add opal calls for opencapi (Steve Best) [1396036]
- [powerpc] powernv: Set correct configuration space size for opencapi devices (Steve Best) [1396036]
- [powerpc] powernv: Introduce new PHB type for opencapi links (Steve Best) [1396036]
- [netdrv] ibmvnic: Do not notify peers on parameter change resets (Steve Best) [1566204]
- [netdrv] ibmvnic: Handle all login error conditions (Steve Best) [1566204]
- [tools] perf vendor events: Update POWER9 events (Steve Best) [1564109]

* Tue Apr 17 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-58.el7a]
- [net] route: check sysctl_fib_multipath_use_neigh earlier than hash (Xin Long) [1562690]
- [net] vti4: Don't override MTU passed on link creation via IFLA_MTU (Stefano Brivio) [1557260]
- [net] ip_tunnel: Clamp MTU to bounds on new link (Stefano Brivio) [1557260]
- [net] vti4: Don't count header length twice on tunnel setup (Stefano Brivio) [1557263]
- [net] vti6: Properly adjust vti6 MTU from MTU of lower device (Stefano Brivio) [1557266]
- [net] ip6_vti: adjust vti mtu according to mtu of lower device (Stefano Brivio) [1557266]
- [net] ip6_gre: init dev->mtu and dev->hard_header_len correctly (Stefano Brivio) [1549464]
- [net] sit: fix IFLA_MTU ignored on NEWLINK (Xin Long) [1549462]
- [net] ip6_tunnel: fix IFLA_MTU ignored on NEWLINK (Xin Long) [1549466]
- [net] ip_gre: fix IFLA_MTU ignored on NEWLINK (Xin Long) [1549467]
- [net] sctp: verify size of a new chunk in _sctp_make_chunk() (Stefano Brivio) [1551905] {CVE-2018-5803}
- [net] netfilter: add back stackpointer size checks (Florian Westphal) [1550791] {CVE-2018-1065}
- [net] sctp: make use of pre-calculated len (Xin Long) [1544628]
- [net] sctp: add a ceiling to optlen in some sockopts (Xin Long) [1544628]
- [net] sctp: GFP_ATOMIC is not needed in sctp_setsockopt_events (Xin Long) [1544628]
- [net] fib_semantics: Don't match route with mismatching tclassid (Stefano Brivio) [1539581]
- [net] ip_gre: remove the incorrect mtu limit for ipgre tap (Xin Long) [1526898]
- [net] ip6_gre: remove the incorrect mtu limit for ipgre tap (Xin Long) [1526898]
- [net] ip6_tunnel: allow ip6gre dev mtu to be set below 1280 (Xin Long) [1526896]
- [net] ip6_tunnel: get the min mtu properly in ip6_tnl_xmit (Xin Long) [1524769]
- [net] sit: update frag_off info (Hangbin Liu) [1523120]

* Fri Apr 13 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-57.el7a]
- [arm64] Kill PSCI_GET_VERSION as a variant-2 workaround (Mark Langsdorf) [1543628]
- [arm64] Add ARM_SMCCC_ARCH_WORKAROUND_1 BP hardening support (Mark Langsdorf) [1543628]
- [firmware] firmware/psci: Expose SMCCC version through psci_ops (Mark Langsdorf) [1543628]
- [firmware] firmware/psci: Expose PSCI conduit (Mark Langsdorf) [1543628]
- [arm64] KVM: Add SMCCC_ARCH_WORKAROUND_1 fast handling (Mark Langsdorf) [1543628]
- [arm64] KVM: Report SMCCC_ARCH_WORKAROUND_1 BP hardening support (Mark Langsdorf) [1543628]
- [arm64] arm/arm64: KVM: Consolidate the PSCI include files (Mark Langsdorf) [1543628]
- [arm64] KVM: Increment PC after handling an SMC trap (Mark Langsdorf) [1543628]
- [arm64] entry: Apply BP hardening for suspicious interrupts from EL0 (Mark Langsdorf) [1543628]

* Thu Apr 12 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-56.el7a]
- [fs] nfsd: remove blocked locks on client teardown (Scott Mayhew) [1565450]
- [fs] nfsd: fix panic in posix_unblock_lock called from nfs4_laundromat (Scott Mayhew) [1565450]
- [fs] ovl: update ctx->pos on impure dir iteration (Thomas Huth) [1561534]
- [misc] cxl: Fix possible deadlock when processing page faults from cxllib (Gustavo Duarte) [1562957]
- [s390] virtio: implement PM operations for virtio_ccw (Cornelia Huck) [1545302]
- [netdrv] ibmvnic: Do not reset CRQ for Mobility driver resets (Steve Best) [1565299]
- [netdrv] ibmvnic: Fix failover case for non-redundant configuration (Steve Best) [1565299]
- [netdrv] ibmvnic: Fix reset scheduler error handling (Steve Best) [1565299]
- [netdrv] ibmvnic: Zero used TX descriptor counter on reset (Steve Best) [1565299]
- [netdrv] ibmvnic: Fix DMA mapping mistakes (Steve Best) [1565299]
- [netdrv] ibmvnic: Disable irqs before exiting reset from closed state (Steve Best) [1565299]
- [netdrv] ibmvnic: Potential NULL dereference in clean_one_tx_pool() (Steve Best) [1565299]
- [powerpc] system reset avoid interleaving oops using die synchronisation (Steve Best) [1564893]
- [powerpc] pseries: Restore default security feature flags on setup (Mauricio Oliveira) [1561784]
- [powerpc] Move default security feature flags (Mauricio Oliveira) [1561784]
- [powerpc] pseries: Fix clearing of security feature flags (Mauricio Oliveira) [1561784]
- [powerpc] 64s: Wire up cpu_show_spectre_v2() (Mauricio Oliveira) [1561784]
- [powerpc] 64s: Wire up cpu_show_spectre_v1() (Mauricio Oliveira) [1561784]
- [powerpc] pseries: Use the security flags in pseries_setup_rfi_flush() (Mauricio Oliveira) [1561784]
- [powerpc] powernv: Use the security flags in pnv_setup_rfi_flush() (Mauricio Oliveira) [1561784]
- [powerpc] 64s: Enhance the information in cpu_show_meltdown() (Mauricio Oliveira) [1561784]
- [powerpc] 64s: Move cpu_show_meltdown() (Mauricio Oliveira) [1561784]
- [powerpc] powernv: Set or clear security feature flags (Mauricio Oliveira) [1561784]
- [powerpc] pseries: Set or clear security feature flags (Mauricio Oliveira) [1561784]
- [powerpc] Add security feature flags for Spectre/Meltdown (Mauricio Oliveira) [1561784]
- [powerpc] pseries: Add new H_GET_CPU_CHARACTERISTICS flags (Mauricio Oliveira) [1561784]
- [powerpc] rfi-flush: Call setup_rfi_flush() after LPM migration (Mauricio Oliveira) [1561783]
- [powerpc] rfi-flush: Differentiate enabled and patched flush types (Mauricio Oliveira) [1561783]
- [powerpc] rfi-flush: Always enable fallback flush on pseries (Mauricio Oliveira) [1561783]
- [powerpc] rfi-flush: Make it possible to call setup_rfi_flush() again (Mauricio Oliveira) [1561783]
- [powerpc] rfi-flush: Move the logic to avoid a redo into the debugfs code (Mauricio Oliveira) [1561783]

* Tue Apr 10 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-55.el7a]
- [sound] ALSA: seq: Fix racy pool initializations (CVE-2018-7566) (Jaroslav Kysela) [1550173] {CVE-2018-7566}
- [pci] PCI: Remove redundant probes for device reset support (Robert Richter) [1553226]
- [pci] PCI: Probe for device reset support during enumeration (Robert Richter) [1553226]
- [char] tpm: use tpm_msleep() value as max delay (Gustavo Duarte) [1562726]
- [char] tpm: reduce tpm polling delay in tpm_tis_core (Gustavo Duarte) [1562726]
- [char] tpm: move wait_for_tpm_stat() to respective driver files (Gustavo Duarte) [1562726]
- [netdrv] ibmvnic: Remove unused TSO resources in TX pool structure (Steve Best) [1559634]
- [netdrv] ibmvnic: Update TX pool cleaning routine (Steve Best) [1559634]
- [netdrv] ibmvnic: Improve TX buffer accounting (Steve Best) [1559634]
- [netdrv] ibmvnic: Update TX and TX completion routines (Steve Best) [1559634]
- [netdrv] ibmvnic: Update TX pool initialization routine (Steve Best) [1559634]
- [netdrv] ibmvnic: Update release TX pool routine (Steve Best) [1559634]
- [netdrv] ibmvnic: Update and clean up reset TX pool routine (Steve Best) [1559634]
- [netdrv] ibmvnic: Generalize TX pool structure (Steve Best) [1559634]
- [netdrv] ibmvnic: Fix reset return from closed state (Steve Best) [1559634]
- [netdrv] ibmvnic: Fix recent errata commit (Steve Best) [1559634]
- [netdrv] ibmvnic: Handle TSO backing device errata (Steve Best) [1559634]
- [netdrv] ibmvnic: Pad small packets to minimum MTU size (Steve Best) [1559634]
- [netdrv] ibmvnic: Account for VLAN header length in TX buffers (Steve Best) [1559634]
- [netdrv] ibmvnic: Account for VLAN tag in L2 Header descriptor (Steve Best) [1559634]
- [netdrv] ibmvnic: Do not disable device during failover or partition migration (Steve Best) [1559634]
- [netdrv] ibmvnic: Reorganize device close (Steve Best) [1559634]
- [netdrv] ibmvnic: Clean up device close (Steve Best) [1559634]
- [powerpc] watchdog: remove arch_trigger_cpumask_backtrace (Gustavo Duarte) [1562287]
- [powerpc] 64s: return more carefully from sreset NMI (Gustavo Duarte) [1562287]

* Tue Apr 10 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-54.el7a]
- [i2c] Make i2c_unregister_device() NULL-aware (Tony Camuso) [1544902]
- [char] ipmi_ssif: Remove duplicate NULL check (Tony Camuso) [1544902]
- [char] ipmi/powernv: Fix error return code in ipmi_powernv_probe() (Tony Camuso) [1544902]
- [char] ipmi: use dynamic memory for DMI driver override (Tony Camuso) [1544902]
- [char] ipmi/ipmi_powernv: remove outdated todo in powernv IPMI driver (Tony Camuso) [1544902]
- [char] ipmi: Clear smi_info->thread to prevent use-after-free during module unload (Tony Camuso) [1544902]
- [char] ipmi: use correct string length (Tony Camuso) [1544902]
- [char] ipmi_si: Fix error handling of platform device (Tony Camuso) [1544902]
- [char] ipmi watchdog: fix typo in parameter description (Tony Camuso) [1544902]
- [char] ipmi_si_platform: Fix typo in parameter description (Tony Camuso) [1544902]
- [char] ipmi_si: fix crash on parisc (Tony Camuso) [1544902]
- [char] ipmi_si: Fix oops with PCI devices (Tony Camuso) [1544902]
- [char] ipmi: Stop timers before cleaning up the module (Tony Camuso) [1544902]
- [char] ipmi: get rid of pointless access_ok() (Tony Camuso) [1544902]
- [char] ipmi_si: Delete an error message for a failed memory allocation in try_smi_init() (Tony Camuso) [1544902]
- [char] ipmi_si: fix memory leak on new_smi (Tony Camuso) [1544902]
- [char] ipmi: remove redundant initialization of bmc (Tony Camuso) [1544902]
- [char] ipmi: pr_err() strings should end with newlines (Tony Camuso) [1544902]
- [char] ipmi: Clean up some print operations (Tony Camuso) [1544902]
- [char] ipmi: Make the DMI probe into a generic platform probe (Tony Camuso) [1544902]
- [char] ipmi: Make the IPMI proc interface configurable (Tony Camuso) [1544902]
- [char] ipmi_ssif: Add device attrs for the things in proc (Tony Camuso) [1544902]
- [char] ipmi_si: Add device attrs for the things in proc (Tony Camuso) [1544902]
- [char] ipmi_si: remove ipmi_smi_alloc() function (Tony Camuso) [1544902]
- [char] ipmi_si: Move port and mem I/O handling to their own files (Tony Camuso) [1544902]
- [char] ipmi_si: Get rid of unused spacing and port fields (Tony Camuso) [1544902]
- [char] ipmi_si: Move PARISC handling to another file (Tony Camuso) [1544902]
- [char] ipmi_si: Move PCI setup to another file (Tony Camuso) [1544902]
- [char] ipmi_si: Move platform device handling to another file (Tony Camuso) [1544902]
- [char] ipmi_si: Move hardcode handling to a separate file (Tony Camuso) [1544902]
- [char] ipmi_si: Move the hotmod handling to another file (Tony Camuso) [1544902]
- [char] ipmi_si: Change ipmi_si_add_smi() to take just I/O info (Tony Camuso) [1544902]
- [char] ipmi_si: Move io setup into io structure (Tony Camuso) [1544902]
- [char] ipmi_si: Move irq setup handling into the io struct (Tony Camuso) [1544902]
- [char] ipmi_si: Move some platform data into the io structure (Tony Camuso) [1544902]
- [char] ipmi_si: Rename function to add smi, make it global (Tony Camuso) [1544902]
- [char] ipmi: Convert IPMI GUID over to Linux guid_t (Tony Camuso) [1544902]
- [char] ipmi: Rescan channel list on BMC changes (Tony Camuso) [1544902]
- [char] ipmi: Move lun and address out of channel struct (Tony Camuso) [1544902]
- [char] ipmi: Retry BMC registration on a failure (Tony Camuso) [1544902]
- [char] ipmi: Rework device id and guid handling to catch changing BMCs (Tony Camuso) [1544902]
- [char] ipmi: Use a temporary BMC for an interface (Tony Camuso) [1544902]
- [char] ipmi: Dynamically fetch GUID periodically (Tony Camuso) [1544902]
- [char] ipmi: Always fetch the guid through ipmi_get_device_id() (Tony Camuso) [1544902]
- [char] ipmi: Remove the device id from ipmi_register_smi() (Tony Camuso) [1544902]
- [char] ipmi: allow dynamic BMC version information (Tony Camuso) [1544902]
- [char] ipmi: Don't use BMC product/dev ids in the BMC name (Tony Camuso) [1544902]
- [char] ipmi: Make ipmi_demangle_device_id more generic (Tony Camuso) [1544902]
- [char] ipmi: Add a reference from BMC devices to their interfaces (Tony Camuso) [1544902]
- [char] ipmi: Get the device id through a function (Tony Camuso) [1544902]
- [char] ipmi: Fix printing the BMC guid (Tony Camuso) [1544902]
- [char] ipmi: Rework BMC registration (Tony Camuso) [1544902]
- [char] ipmi: Prefer ACPI system interfaces over SMBIOS ones (Tony Camuso) [1544902]
- [char] ipmi: Fix issues with BMC refcounts (Tony Camuso) [1544902]
- [char] ipmi: Check that the device type is BMC when scanning device (Tony Camuso) [1544902]
- [char] ipmi: Move bmc find routing to below bmc device type (Tony Camuso) [1544902]
- [char] ipmi: Fix getting the GUID data (Tony Camuso) [1544902]
- [char] IPMI: make ipmi_poweroff_handler const (Tony Camuso) [1544902]
- [char] ipmi: Make IPMI panic strings always available (Tony Camuso) [1544902]
- [char] ipmi: make function ipmi_get_info_from_resources static (Tony Camuso) [1544902]
- [char] ipmi: fix unsigned long underflow (Tony Camuso) [1544902]
- [char] ipmi: eliminate misleading print info when being probed via ACPI (Tony Camuso) [1544902]

* Thu Apr 05 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-53.el7a]
- [md] dm btree: fix serious bug in btree_split_beneath() (Mike Snitzer) [1559487]
- [perf] arm_pmu: acpi: request IRQs up-front (Mark Salter) [1460336]
- [perf] arm_pmu: note IRQs and PMUs per-cpu (Mark Salter) [1460336]
- [perf] arm_pmu: explicitly enable/disable SPIs at hotplug (Mark Salter) [1460336]
- [perf] arm_pmu: acpi: check for mismatched PPIs (Mark Salter) [1460336]
- [perf] arm_pmu: add armpmu_alloc_atomic() (Mark Salter) [1460336]
- [perf] arm_pmu: fold platform helpers into platform code (Mark Salter) [1460336]
- [perf] arm_pmu: kill arm_pmu_platdata (Mark Salter) [1460336]
- [perf] arm/arm64: pmu: Distinguish percpu irq and percpu_devid irq (Mark Salter) [1460336]
- [kernel] irqdesc: Add function to identify percpu_devid irqs (Mark Salter) [1460336]
- [irqchip] irqchip/gic-v3: Change pr_debug message to pr_devel (Mark Salter) [1519901]

* Wed Apr 04 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-52.el7a]
- [misc] cxl: Fix timebase synchronization status on P9 (Steve Best) [1558675]
- [powerpc] kvm: ppc: book3s hv: Fix duplication of host SLB entries (Gustavo Duarte) [1559812]
- [powerpc] 64s: Fix lost pending interrupt due to race causing lost update to irq_happened (Steve Best) [1558661]
- [powerpc] cxl: read PHB indications from the device tree (Steve Best) [1558675 1553205]
- [powerpc] powerpc/powernv: Enable tunneled operations (Steve Best) [1558675 1553205]
- [powerpc] mm: Fixup tlbie vs store ordering issue on POWER9 (Mauricio Oliveira) [1559636]
- [powerpc] mm/radix: Move the functions that does the actual tlbie closer (Mauricio Oliveira) [1559636]
- [powerpc] mm/radix: Remove unused code (Mauricio Oliveira) [1559636]
- [powerpc] powernv: Fix kexec crashes caused by tlbie tracing (Mauricio Oliveira) [1559636]
- [powerpc] 64s/radix: Optimize TLB range flush barriers (Mauricio Oliveira) [1559636]
- [powerpc] npu-dma.c: Fix crash after __mmu_notifier_register failure (Mauricio Oliveira) [1559636]
- [powerpc] powernv/npu: Fix deadlock in mmio_invalidate() (Mauricio Oliveira) [1559636]
- [powerpc] mm: Workaround Nest MMU bug with TLB invalidations (Mauricio Oliveira) [1559636]
- [powerpc] mm: Add tracking of the number of coprocessors using a context (Mauricio Oliveira) [1559636]
- [powerpc] powernv/npu: Don't explicitly flush nmmu tlb (Mauricio Oliveira) [1559636]
- [powerpc] powernv/npu: Use flush_all_mm() instead of flush_tlb_mm() (Mauricio Oliveira) [1559636]

* Tue Apr 03 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-51.el7a]
- [netdrv] net: thunder: change q_len's type to handle max ring size (Dean Nelson) [1489767]
- [netdrv] net: ethernet: cavium: Correct Cavium Thunderx NIC driver names accordingly to module name (Vadim Lomovtsev) [1490798]
- [netdrv] ibmvnic: Do not attempt to login if RX or TX queues are not allocated (Steve Best) [1552019]
- [netdrv] ibmvnic: Report queue stops and restarts as debug output (Steve Best) [1552019]
- [netdrv] ibmvnic: Harden TX/RX pool cleaning (Steve Best) [1552019]
- [netdrv] ibmvnic: Allocate statistics buffers during probe (Steve Best) [1552019]
- [netdrv] ibmvnic: Fix TX descriptor tracking again (Steve Best) [1552019]
- [netdrv] ibmvnic: Split counters for scrq/pools/napi (Steve Best) [1546655]
- [netdrv] ibmvnic: Fix TX descriptor tracking (Steve Best) [1546655]
- [netdrv] ibmvnic: Fix early release of login buffer (Steve Best) [1546655]
- [netdrv] ibmvnic: Correct goto target for tx irq initialization failure (Steve Best) [1546655]
- [netdrv] ibmvnic: Allocate max queues stats buffers (Steve Best) [1546655]
- [netdrv] ibmvnic: Make napi usage dynamic (Steve Best) [1546655]
- [netdrv] ibmvnic: Free and re-allocate scrqs when tx/rx scrqs change (Steve Best) [1546655]
- [netdrv] ibmvnic: Move active sub-crq count settings (Steve Best) [1546655]
- [netdrv] ibmvnic: Rename active queue count variables (Steve Best) [1546655]
- [netdrv] ibmvnic: Check for NULL skb's in NAPI poll routine (Steve Best) [1546655]
- [netdrv] ibmvnic: Keep track of supplementary TX descriptors (Steve Best) [1546655]
- [netdrv] ibmvnic: Clean RX pool buffers during device close (Steve Best) [1545572]
- [netdrv] ibmvnic: Free RX socket buffer in case of adapter error (Steve Best) [1545572]
- [netdrv] ibmvnic: Fix NAPI structures memory leak (Steve Best) [1545572]
- [netdrv] ibmvnic: Fix login buffer memory leaks (Steve Best) [1545572]
- [netdrv] ibmvnic: Wait until reset is complete to set carrier on (Steve Best) [1545572]

* Thu Mar 29 2018 Rafael Aquini <aquini@redhat.com> [4.14.0-50.el7a]
- [redhat] makefile: bump RHEL_MINOR to 6 (Rafael Aquini)
- [redhat] switch secureboot kernel signing back to devel key (Rafael Aquini)
- [redhat] update RHMAINTAINERS (Rafael Aquini)
- [redhat] fix NVMe hotplug failure on some platforms (Steve Ulrich) [1557004]
- [netdrv] i40e: Fix attach VF to VM issue (Stefan Assmann) [1516619]
- [block] loop: fix concurrent lo_open/lo_release (Joe Lawrence) [1541232] {CVE-2018-5344}
- [fs] NFS: Fix unstable write completion (Scott Mayhew) [1552471]
- [scsi] csiostor: add support for 32 bit port capabilities (Arjun Vynipadath) [1547715]
- [misc] cxl: Check if vphb exists before iterating over AFU devices (Steve Best) [1553052]
- [nvme] nvme-pci: Fix queue double allocations (David Milburn) [1555296]
- [nvme] nvme-pci: Fix EEH failure on ppc (David Milburn) [1554747]
- [s390] KVM: s390: take care of clock-comparator sign control (Thomas Huth) [1555263]
- [s390] KVM: s390: consider epoch index on hotplugged CPUs (Thomas Huth) [1555263]
- [s390] KVM: s390: consider epoch index on TOD clock syncs (Thomas Huth) [1555263]
- [s390] KVM: s390: provide only a single function for setting the tod (fix SCK) (Thomas Huth) [1555263]
- [powerpc] KVM: PPC: Book3S HV: Fix trap number return from __kvmppc_vcore_entry (Laurent Vivier) [1555068]
- [powerpc] KVM: PPC: Book3S HV: Fix VRMA initialization with 2MB or 1GB memory backing (Laurent Vivier) [1552768]
- [powerpc] KVM: PPC: Book3S HV: Fix handling of large pages in radix page fault handler (Laurent Vivier) [1549933]
- [powerpc] powerpc/64s: Fix NULL AT_BASE_PLATFORM when using DT CPU features (Steve Best) [1555236]
- [powerpc] KVM: PPC: Book3S PR: Fix WIMG handling under pHyp (Laurent Vivier) [1553158]
- [powerpc] Fix DABR match on hash based systems (Steve Best) [1552080]
- [powerpc] powerpc/powernv: Support firmware disable of RFI flush (Mauricio Oliveira) [1554920]
- [powerpc] powerpc/pseries: Support firmware disable of RFI flush (Mauricio Oliveira) [1554920]
- [watchdog] sbsa: use 32-bit read for WCV (Robert Richter) [1553237]

* Wed Mar 14 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-49.el7a]
- [netdrv] tg3: prevent scheduling while atomic splat (Jonathan Toppins) [1555032]
- [powerpc] KVM: PPC: Book3S HV: Fix guest time accounting with VIRT_CPU_ACCOUNTING_GEN (Laurent Vivier) [1541614]
- [powerpc] KVM: PPC: Book3S HV: Improve handling of debug-trigger HMIs on POWER9 (Gustavo Duarte) [1548423]

* Tue Mar 06 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-48.el7a]
- [s390] s390/entry.S: fix spurious zeroing of r0 (Hendrik Brueckner) [1551586]

* Mon Mar 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-47.el7a]
- [kernel] futex: Prevent overflow by strengthen input validation (Joe Lawrence) [1547583] {CVE-2018-6927}

* Mon Feb 26 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-46.el7a]
- [powerpc] ppc needs macro for spectre v1 mitigation (Christoph von Recklinghausen) [1538186]
- [arm64] Add missing Falkor part number for branch predictor hardening (Spectre/Meltdown) (Steve Ulrich) [1545916]
- [s390] kernel: fix rwlock implementation (Hendrik Brueckner) [1547423]
- [redhat] s390/configs: enable KERNEL_NOBP for s390 (Hendrik Brueckner) [1532726]
- [s390] spinlock: add __nospec_barrier memory barrier (Hendrik Brueckner) [1532726]
- [s390] Replace IS_ENABLED(EXPOLINE_*) with IS_ENABLED(CONFIG_EXPOLINE_*) (Hendrik Brueckner) [1532726]
- [s390] introduce execute-trampolines for branches (Hendrik Brueckner) [1532726]
- [s390] run user space and KVM guests with modified branch prediction (Hendrik Brueckner) [1532726]
- [s390] add options to change branch prediction behaviour for the kernel (Hendrik Brueckner) [1532726]
- [s390] s390/alternative: use a copy of the facility bit mask (Hendrik Brueckner) [1532726]
- [s390] add optimized array_index_mask_nospec (Hendrik Brueckner) [1532726]
- [s390] scrub registers on kernel entry and KVM exit (Hendrik Brueckner) [1532726]
- [s390] enable CPU alternatives unconditionally (Hendrik Brueckner) [1532726]
- [s390] introduce CPU alternatives (Hendrik Brueckner) [1532726]
- [security] KEYS: Use individual pages in big_key for crypto buffers (David Howells) [1510601]
- [powerpc] powerpc/eeh: Fix crashes in eeh_report_resume() (Gustavo Duarte) [1546028]
- [redhat] switch secureboot kernel image signing to release keys ("Herton R. Krzesinski")
- [redhat] RHMAINTAINERS: update power management sections (Al Stone)
- [fs] xfs: validate sb_logsunit is a multiple of the fs blocksize (Bill O'Donnell) [1538496]
- [kernel] bpf: prevent out-of-bounds speculation (Mark Langsdorf) [1536036]
- [arm64] kpti: Fix the interaction between ASID switching and software PAN (Mark Langsdorf) [1536036]
- [arm64] SW PAN: Point saved ttbr0 at the zero page when switching to init_mm (Mark Langsdorf) [1536036]
- [arm64] Re-order reserved_ttbr0 in linker script (Mark Langsdorf) [1536036]
- [arm64] capabilities: Handle duplicate entries for a capability (Mark Langsdorf) [1536036]

* Tue Feb 20 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-45.el7a]
- [netdrv] tg3: APE heartbeat changes (Jonathan Toppins) [1545870]
- [redhat] fix rh_get_maintainer.pl (Andrew Jones)
- [scsi] lpfc Fix SCSI io host reset causing kernel crash (Dick Kennedy) [1540693]

* Mon Feb 19 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-44.el7a]
- [powerpc] powerpc/mm: Flush radix process translations when setting MMU type (Laurent Vivier) [1533718]
- [powerpc] powerpc/mm/radix: Split linear mapping on hot-unplug (Suraj Jitindar Singh) [1516201]
- [powerpc] KVM: PPC: Book3S: Add MMIO emulation for VMX instructions (Laurent Vivier) [1537935]
- [powerpc] KVM: PPC: Book3S HV: Make HPT resizing work on POWER9 (Laurent Vivier) [1535789]
- [powerpc] KVM: PPC: Book3S HV: Fix handling of secondary HPTEG in HPT resizing code (Laurent Vivier) [1535789]
- [powerpc] KVM: PPC: Book3S HV: Drop locks before reading guest memory (Laurent Vivier) [1540077]
- [powerpc] powerpc/64s/radix: Boot-time NULL pointer protection using a guard-PID (Mauricio Oliveira) [1539109]
- [block] blk-mq-debugfs: don't allow write on attributes with seq_operations set (Ming Lei) [1543463]
- [fs] dcache: Revert manually unpoison dname after allocation to shut up kasan's reports (Joe Lawrence) [1539609]
- [fs] fs/dcache: Use read_word_at_a_time() in dentry_string_cmp() (Joe Lawrence) [1539609]
- [lib] lib/strscpy: Shut up KASAN false-positives in strscpy() (Joe Lawrence) [1539609]
- [kernel] compiler.h: Add read_word_at_a_time() function (Joe Lawrence) [1539609]
- [kernel] compiler.h, kasan: Avoid duplicating __read_once_size_nocheck() (Joe Lawrence) [1539609]
- [redhat] update handling for our additional certificates ("Herton R. Krzesinski") [1539015]
- [redhat] make CONFIG_MODULE_SIG_SHA* common through all architectures ("Herton R. Krzesinski") [1539015]
- [redhat] remove extra_certificates file ("Herton R. Krzesinski") [1539015]
- [fs] xfs: truncate pagecache before writeback in xfs_setattr_size() (Bill O'Donnell) [1518553]
- [fs] autofs: revert autofs: take more care to not update last_used on path walk (Ian Kent) [1535760]

* Sat Feb 17 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-43.el7a]
- [netdrv] sfc: don't warn on successful change of MAC (Jarod Wilson) [1448760]
- [netdrv] ibmvnic: Remove skb->protocol checks in ibmvnic_xmit (Steve Best) [1544017]
- [netdrv] ibmvnic: Reset long term map ID counter (Steve Best) [1544017]
- [scsi] qla2xxx: Update driver version to 10.00.00.01.07.5a-k1 (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Fix memory corruption during hba reset test (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Fix logo flag for qlt_free_session_done() (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Fix NULL pointer crash due to probe failure (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Defer processing of GS IOCB calls (Himanshu Madhani) [1542778]
- [nvme] nvme-pci: allocate device queues storage space at probe (Ming Lei) [1523270]
- [kernel] include/linux/slab.h: add kmalloc_array_node() and kcalloc_node() (Ming Lei) [1523270]
- [nvme] nvme-pci: serialize pci resets (Ming Lei) [1523494]
- [block] blk-mq: fix race between updating nr_hw_queues and switching io sched (Ming Lei) [1523270]
- [block] blk-mq: avoid to map CPU into stale hw queue (Ming Lei) [1523270]
- [block] blk-mq: quiesce queue during switching io sched and updating nr_requests (Ming Lei) [1523270]
- [block] blk-mq: quiesce queue before freeing queue (Ming Lei) [1523270]
- [block] blk-mq: only run the hardware queue if IO is pending (Ming Lei) [1523270]
- [block] Fix a race between blk_cleanup_queue() and timeout handling (Ming Lei) [1538482]

* Fri Feb 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-42.el7a]
- [net] sched: cbq: create block for q->link.block (Davide Caratti) [1544314]
- [net] cls_u32: fix use after free in u32_destroy_key() (Paolo Abeni) [1516696]
- [net] netfilter: xt_osf: Add missing permission checks (Florian Westphal) [1539229] {CVE-2017-17448}
- [net] netfilter: nfnetlink_cthelper: Add missing permission checks (Florian Westphal) [1539229] {CVE-2017-17448}

* Mon Feb 12 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-41.el7a]
- [netdrv] ibmvnic: queue reset when CRQ gets closed during reset (Steve Best) [1543729]
- [kernel] modules: add rhelversion MODULE_INFO tag (Prarit Bhargava) [1542796]
- [kernel] put RHEL info into generated headers (Prarit Bhargava) [1542796]
- [netdrv] ibmvnic: Ensure that buffers are NULL after free (Steve Best) [1543713]
- [netdrv] ibmvnic: fix empty firmware version and errors cleanup (Steve Best) [1543713]
- [powerpc] powerpc/64s: Allow control of RFI flush via debugfs (Mauricio Oliveira) [1543083]
- [powerpc] powerpc/64s: Improve RFI L1-D cache flush fallback (Mauricio Oliveira) [1543083]
- [powerpc] powerpc/xmon: Add RFI flush related fields to paca dump (Mauricio Oliveira) [1543083]
- [powerpc] powerpc/64s: Wire up cpu_show_meltdown() (Mauricio Oliveira) [1543083]
- [base] sysfs/cpu: Add vulnerability folder (Mauricio Oliveira) [1543083]
- [scsi] aacraid: Fix udev inquiry race condition (Gustavo Duarte) [1541141]
- [scsi] aacraid: Do not attempt abort when Fw panicked (Gustavo Duarte) [1541141]
- [scsi] aacraid: Fix hang in kdump (Gustavo Duarte) [1541141]
- [scsi] aacraid: Do not remove offlined devices (Gustavo Duarte) [1541141]
- [scsi] aacraid: Fix ioctl reset hang (Gustavo Duarte) [1541141]
- [redhat] configs: enable CONFIG_USERFAULTFD on s390x (David Hildenbrand) [1540679]
- [pci] PCI/AER: Skip recovery callbacks for correctable errors from ACPI APEI (Steve Ulrich) [1495258]

* Sun Feb 11 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-40.el7a]
- [char] crash driver: fix probe_kernel_read() failure to return -EFAULT (Dave Anderson) [1533712]
- [netdrv] ibmvnic: Fix rx queue cleanup for non-fatal resets (Steve Best) [1543315]
- [scsi] libcxgbi: use GFP_ATOMIC in cxgbi_conn_alloc_pdu() (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: when flushing, complete all wrs in a chain (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: reflect the original WR opcode in drain cqes (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: Only validate the MSN for successful completions (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: only insert drain cqes if wq is flushed (Arjun Vynipadath) [1541086]
- [usb] USB: core: prevent malicious bNumInterfaces overflow (Torez Smith) [1536888] {CVE-2017-17558}
- [acpi] ACPI: APEI: call into AER handling regardless of severity (Al Stone) [1403771 1288440 1268474]
- [acpi] ACPI: APEI: handle PCIe AER errors in separate function (Al Stone) [1403771 1288440 1268474]
- [i2c] xlp9xx: Check for Bus state after every transfer (Robert Richter) [1504298]
- [i2c] xlp9xx: report SMBus block read functionality (Robert Richter) [1504298]
- [i2c] xlp9xx: Handle transactions with I2C_M_RECV_LEN properly (Robert Richter) [1504298]
- [i2c] xlp9xx: return ENXIO on slave address NACK (Robert Richter) [1504298]
- [acpi] ACPI / APD: Add clock frequency for ThunderX2 I2C controller (Robert Richter) [1504298]
- [i2c] xlp9xx: Get clock frequency with clk API (Robert Richter) [1504298]
- [i2c] xlp9xx: Handle I2C_M_RECV_LEN in msg->flags (Robert Richter) [1504298]
- [pci] quirk: adding Ampere vendor id to ACS quirk list (Iyappan Subramanian) [1539204]
- [fs] disable unsupported new disk formats again (Eric Sandeen) [1514234]

* Thu Feb 08 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-39.el7a]
- [scsi] mpt3sas: fix an out of bound write (Desnes Augusto Nunes do Rosario) [1503961]
- [netdrv] ibmvnic: fix firmware version when no firmware level has been provided by the VIOS server (Steve Best) [1541322]
- [powerpc] powerpc/pseries: Add Initialization of VF Bars (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pseries/pci: Associate PEs to VFs in configure SR-IOV (Gustavo Duarte) [1539902]
- [powerpc] powerpc/eeh: Add EEH notify resume sysfs (Gustavo Duarte) [1539902]
- [powerpc] powerpc/eeh: Add EEH operations to notify resume (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pseries: Set eeh_pe of EEH_PE_VF type (Gustavo Duarte) [1539902]
- [pci] PCI/AER: Add uevents in AER and EEH error/resume (Gustavo Duarte) [1539902]
- [powerpc] powerpc/eeh: Update VF config space after EEH (Gustavo Duarte) [1539902]
- [pci] PCI/IOV: Add pci_vf_drivers_autoprobe() interface (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pseries: Add pseries SR-IOV Machine dependent calls (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pci: Separate SR-IOV Calls (Gustavo Duarte) [1539902]
- [edac] EDAC, sb_edac: Don't create a second memory controller if HA1 is not present (Aristeu Rozanski) [1513814]
- [infiniband] iser-target: avoid reinitializing rdma contexts for isert commands (Jonathan Toppins) [1540435]
- [netdrv] cxgb4: fix possible deadlock (Arjun Vynipadath) [1540018]
- [fs] nfs: don't wait on commit in nfs_commit_inode() if there were no commit requests (Scott Mayhew) [1538083]
- [tools] perf help: Fix a bug during strstart() conversion (Jiri Olsa) [1513107]
- [s390] s390x, crash driver: verify RAM page with probe_kernel_read() (Dave Anderson) [1533712]
- [kernel] lockdep: Increase MAX_STACK_TRACE_ENTRIES for debug kernel (Waiman Long) [1483161]

* Mon Feb 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-38.el7a]
- [ata] fixes kernel crash while tracing ata_eh_link_autopsy event (David Milburn) [1540760]
- [powerpc] KVM: PPC: Book3S: Provide information about hardware/firmware CVE workarounds (Serhii Popovych) [1532074]
- [netdrv] ibmvnic: Wait for device response when changing MAC (Steve Best) [1540839]
- [kernel] kdump: print kdump kernel loaded status in stack dump (Lianbo Jiang) [1535756]
- [netdrv] i40e: restore promiscuous after reset (Stefan Assmann) [1517973]
- [powerpc] KVM: PPC: Book3S HV: Allow HPT and radix on the same core for POWER9 v2.2 (Sam Bobroff) [1535753]
- [powerpc] KVM: PPC: Book3S HV: Do SLB load/unload with guest LPCR value loaded (Sam Bobroff) [1535753]
- [powerpc] KVM: PPC: Book3S HV: Make sure we don't re-enter guest without XIVE loaded (Sam Bobroff) [1535753]
- [sound] ALSA: seq: Make ioctls race-free (CVE-2018-1000004) (Jaroslav Kysela) [1537204] {CVE-2018-1000004}

* Thu Feb 01 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-37.el7a]
- [md] dm mpath: remove annoying message of 'blk_get_request() returned -11' (Gustavo Duarte) [1539251]
- [net] kernel: Missing namespace check in net/netlink/af_netlink.c allows for network monitors to observe systemwide activity (William Townsend) [1538736] {CVE-2017-17449}
- [s390] KVM: s390: wire up bpb feature (David Hildenbrand) [1539637]
- [iommu] iommu/arm-smmu-v3: Cope with duplicated Stream IDs (Robert Richter) [1529518]
- [mm] mm/mprotect: add a cond_resched() inside change_pmd_range() (Desnes Augusto Nunes do Rosario) [1535916]
- [s390] s390/mm: fix off-by-one bug in 5-level page table handling (Oleg Nesterov) [1517792]

* Wed Jan 31 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-36.el7a]
- [powerpc] Don't preempt_disable() in show_cpuinfo() (Gustavo Duarte) [1517679]
- [powerpc] powerpc/powernv/cpufreq: Fix the frequency read by /proc/cpuinfo (Gustavo Duarte) [1517679]
- [drm] drm/ttm: add ttm_bo_io_mem_pfn to check io_mem_pfn (Zhou Wang) [1502558]

* Tue Jan 30 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-35.el7a]
- [powerpc] powerpc/mm: Invalidate subpage_prot() system call on radix platforms (Steve Best) [1538328]
- [arm64] Turn on KPTI only on CPUs that need it (Vadim Lomovtsev) [1537982]
- [arm64] Branch predictor hardening for Cavium ThunderX2 (Vadim Lomovtsev) [1537982]
- [arm64] cputype: Add MIDR values for Cavium ThunderX2 CPUs (Vadim Lomovtsev) [1537982]
- [redhat] use recently created brew target for rhel-alt kernel signing ("Herton R. Krzesinski") [1492103]
- [virt] KVM: arm/arm64: kvm_arch_destroy_vm cleanups (Auger Eric) [1536027]
- [virt] KVM: arm/arm64: vgic: Move kvm_vgic_destroy call around (Auger Eric) [1536027]
- [arm64] KVM: Fix SMCCC handling of unimplemented SMC/HVC calls (Auger Eric) [1536027]
- [virt] KVM: arm64: Fix GICv4 init when called from vgic_its_create (Auger Eric) [1536027]
- [virt] KVM: arm/arm64: Check pagesize when allocating a hugepage at Stage 2 (Auger Eric) [1536027]
- [scsi] mpt3sas: Bump driver version (Julius Milan) [1524723]
- [scsi] mpt3sas: Reduce memory footprint in kdump kernel (Julius Milan) [1524723]
- [scsi] mpt3sas: Fixed memory leaks in driver (Julius Milan) [1524723]
- [scsi] mpt3sas: remove redundant copy_from_user in _ctl_getiocinfo (Julius Milan) [1524723]

* Mon Jan 29 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-34.el7a]
- [netdrv] ibmvnic: Allocate and request vpd in init_resources (Steve Best) [1537431]
- [netdrv] ibmvnic: Revert to previous mtu when unsupported value requested (Steve Best) [1537431]
- [netdrv] ibmvnic: Modify buffer size and number of queues on failover (Steve Best) [1537431]
- [misc] cxl: Add support for ASB_Notify on POWER9 (Steve Best) [1537750]
- [cpuidle] powerpc/pseries/cpuidle: add polling idle for shared processor guests (Steve Best) [1538249]
- [scsi] lpfc: Removing bad lockdep_assert patch (Dick Kennedy) [1482600 1420592 1392037]
- [powerpc] powerpc/spinlock: add gmb memory barrier (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/powernv: Check device-tree for RFI flush settings (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/pseries: Query hypervisor for RFI flush settings (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Support disabling RFI flush with no_rfi_flush and nopti (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Add support for RFI flush of L1-D cache (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Convert slb_miss_common to use RFI_TO_USER/KERNEL (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64: Convert fast_exception_return to use RFI_TO_USER/KERNEL (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64: Convert the syscall exit path to use RFI_TO_USER/KERNEL (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Simple RFI macro conversions (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64: Add macros for annotating the destination of rfid/hrfid (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/pseries: Add H_GET_CPU_CHARACTERISTICS flags & wrapper (Mauricio Oliveira) [1531718]
- [arm64] mm: Fix pte_mkclean, pte_mkdirty semantics (Steve Ulrich) [1512366]

* Fri Jan 26 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-33.el7a]
- [netdrv] ibmvnic: Fix IPv6 packet descriptors (Steve Best) [1536745]
- [netdrv] ibmvnic: Fix IP offload control buffer (Steve Best) [1536745]
- [misc] cxl: Rework the implementation of cxl_stop_trace_psl9() (Steve Best) [1534499]
- [infiniband] IB/core: Verify that QP is security enabled in create and destroy (Kamal Heib) [1533578]
- [net] Bluetooth: Prevent stack info leak from the EFS element (Gopal Tiwari) [1519629] {CVE-2017-1000410}
- [infiniband] IB/mlx5: Fix mlx5_ib_alloc_mr error flow (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Serialize access to the VMA list (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Fix congestion counters in LAG mode (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Stay in polling mode when command EQ destroy fails (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Cleanup IRQs in case of unload failure (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Fix error flow in CREATE_QP command (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Fix RoCE Address Path fields (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Assign send CQ and recv CQ of UMR QP (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Avoid NULL pointer dereference on steering cleanup (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Fix creating a new FTE when an existing but full FTE exists (Kamal Heib) [1536454]
- [netdrv] net/mlx5e: Prevent possible races in VXLAN control flow (Kamal Heib) [1535618]
- [netdrv] net/mlx5e: Add refcount to VXLAN structure (Kamal Heib) [1535618]
- [netdrv] net/mlx5e: Fix possible deadlock of VXLAN lock (Kamal Heib) [1535618]
- [netdrv] net/mlx5e: Fix ETS BW check (Kamal Heib) [1535594]
- [powerpc] powernv/kdump: Fix cases where the kdump kernel can get HMI's (Gustavo Duarte) [1521103]
- [powerpc] powerpc/crash: Remove the test for cpu_online in the IPI callback (Gustavo Duarte) [1521103]
- [fs] autofs: revert fix AT_NO_AUTOMOUNT not being honored (Justin Mitchell) [1517279]

* Wed Jan 24 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-32.el7a]
- [scsi] lpfc: fix kzalloc-simple.cocci warnings (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix hard lock up NMI in els timeout handling (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix a precedence bug in lpfc_nvme_io_cmd_wqe_cmpl() (Dick Kennedy) [1396074]
- [scsi] lpfc: change version to 11.4.0.4 (Dick Kennedy) [1396074]
- [scsi] lpfc: correct nvme sg segment count check (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix oops of nvme host during driver unload (Dick Kennedy) [1396074]
- [scsi] lpfc: Extend RDP support (Dick Kennedy) [1396074]
- [scsi] lpfc: Ensure io aborts interlocked with the target (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix secure firmware updates (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix crash in lpfc_nvme_fcp_io_submit during LIP (Dick Kennedy) [1396074]
- [scsi] lpfc: Disable NPIV support if NVME is enabled (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix oops if nvmet_fc_register_targetport fails (Dick Kennedy) [1396074]
- [scsi] lpfc: Revise NVME module parameter descriptions for better clarity (Dick Kennedy) [1396074]
- [scsi] lpfc: Set missing abort context (Dick Kennedy) [1396074]
- [scsi] lpfc: Reduce log spew on controller reconnects (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix FCP hba_wqidx assignment (Dick Kennedy) [1396074]
- [scsi] lpfc: Move CQ processing to a soft IRQ (Dick Kennedy) [1396074]
- [scsi] lpfc: Make ktime sampling more accurate (Dick Kennedy) [1396074]
- [scsi] lpfc: PLOGI failures during NPIV testing (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix warning messages when NVME_TARGET_FC not defined (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix lpfc nvme host rejecting IO with Not Ready message (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix crash receiving ELS while detaching driver (Dick Kennedy) [1396074]
- [scsi] lpfc: fix pci hot plug crash in list_add call (Dick Kennedy) [1396074]
- [scsi] lpfc: fix pci hot plug crash in timer management routines (Dick Kennedy) [1396074]
- [scsi] lpfc: Cocci spatch pool_zalloc-simple (Dick Kennedy) [1396074]
- [scsi] lpfc: remove redundant null check on eqe (Dick Kennedy) [1396074]

* Wed Jan 24 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-31.el7a]
- [fs] udf: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [fs] vfs, fdtable: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [net] ipv4: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [net] ipv6: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [thermal] Thermal/int340x: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [wireless] cw1200: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [scsi] qla2xxx: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [wireless] p54: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [wireless] carl9170: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [usb] uvcvideo: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [kernel] userns: prevent speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [arm64] implement nospec_ptr() (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [documentation] document nospec helpers (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [kernel] asm-generic/barrier: add generic nospec helpers (Josh Poimboeuf) [1527436] {CVE-2017-5753}

* Tue Jan 23 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-30.el7a]
- [arm64] Implement branch predictor hardening for Falkor (Mark Langsdorf) [1532118]
- [arm64] Implement branch predictor hardening for affected Cortex-A CPUs (Mark Langsdorf) [1532118]
- [arm64] cputype: Add missing MIDR values for Cortex-A72 and Cortex-A75 (Mark Langsdorf) [1532118]
- [arm64] KVM: Make PSCI_VERSION a fast path (Mark Langsdorf) [1532118]
- [arm64] KVM: Use per-CPU vector when BP hardening is enabled (Mark Langsdorf) [1532118]
- [arm64] Add skeleton to harden the branch predictor against aliasing attacks (Mark Langsdorf) [1532118]
- [arm64] Move post_ttbr_update_workaround to C code (Mark Langsdorf) [1532118]
- [firmware] drivers/firmware: Expose psci_get_version through psci_ops structure (Mark Langsdorf) [1532118]
- [arm64] cpufeature: Pass capability structure to ->enable callback (Mark Langsdorf) [1532118]
- [arm64] Take into account ID_AA64PFR0_EL1.CSV3 (Mark Langsdorf) [1532118]
- [arm64] Kconfig: Reword UNMAP_KERNEL_AT_EL0 kconfig entry (Mark Langsdorf) [1532118]
- [arm64] use RET instruction for exiting the trampoline (Mark Langsdorf) [1532118]
- [arm64] entry.S: convert elX_irq (Mark Langsdorf) [1532118]
- [arm64] entry.S convert el0_sync (Mark Langsdorf) [1532118]
- [arm64] entry.S: convert el1_sync (Mark Langsdorf) [1532118]
- [arm64] entry.S: Remove disable_dbg (Mark Langsdorf) [1532118]
- [arm64] Mask all exceptions during kernel_exit (Mark Langsdorf) [1532118]
- [arm64] Move the async/fiq helpers to explicitly set process context flags (Mark Langsdorf) [1532118]
- [arm64] introduce an order for exceptions (Mark Langsdorf) [1532118]
- [arm64] explicitly mask all exceptions (Mark Langsdorf) [1532118]

* Mon Jan 22 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-29.el7a]
- [misc] cxl: Provide debugfs access to PSL_DEBUG/XSL_DEBUG registers (Steve Best) [1534500]
- [cpufreq] powernv-cpufreq: Treat pstates as opaque 8-bit values (Steve Best) [1534472]
- [cpufreq] powernv-cpufreq: Fix pstate_to_idx() to handle non-continguous pstates (Steve Best) [1534472]
- [cpufreq] powernv-cpufreq: Add helper to extract pstate from PMSR (Steve Best) [1534472]
- [net] openvswitch: Fix pop_vlan action for double tagged frames (Eric Garver) [1532639]
- [net] xfrm: Fix stack-out-of-bounds read on socket policy lookup. (Florian Westphal) [1513059]
- [net] xfrm: Forbid state updates from changing encap type (Florian Westphal) [1513059]
- [net] xfrm: Fix stack-out-of-bounds with misconfigured transport mode policies. (Florian Westphal) [1513059]
- [net] xfrm: skip policies marked as dead while rehashing (Florian Westphal) [1513059]
- [net] revert "xfrm: Fix stack-out-of-bounds read in xfrm_state_find." (Florian Westphal) [1513059]
- [net] xfrm: put policies when reusing pcpu xdst entry (Florian Westphal) [1513059]
- [net] xfrm: Copy policy family in clone_policy (Florian Westphal) [1513059]
- [net] netfilter: uapi: correct UNTRACKED conntrack state bit number (Florian Westphal) [1530258]
- [net] netfilter: ip6t_MASQUERADE: add dependency on conntrack module (Florian Westphal) [1527250]
- [net] ipv4: fib: Fix metrics match when deleting a route (Phil Sutter) [1527591]
- [net] ipv4: fix for a race condition in raw_sendmsg (Stefano Brivio) [1527027] {CVE-2017-17712}
- [net] ipv6: remove from fib tree aged out RTF_CACHE dst (Paolo Abeni) [1524275]
- [net] vxlan: fix the issue that neigh proxy blocks all icmpv6 packets (Lorenzo Bianconi) [1523020]
- [net] sched: fix use-after-free in tcf_block_put_ext (Paolo Abeni) [1518144]
- [net] net_sched: get rid of rcu_barrier() in tcf_block_put_ext() (Paolo Abeni) [1518144]
- [net] net_sched: no need to free qdisc in RCU callback (Paolo Abeni) [1518144]
- [net] sched: crash on blocks with goto chain action (Paolo Abeni) [1518144]
- [net] ipv6: set all.accept_dad to 0 by default (Florian Westphal) [1516744]

* Mon Jan 22 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-28.el7a]
- [misc] cxl: Dump PSL_FIR register on PSL9 error irq (Steve Best) [1534493]
- [misc] cxl: Rename register PSL9_FIR2 to PSL9_FIR_MASK (Steve Best) [1534493]
- [crypto] crypto/nx: Do not initialize workmem allocation (Gustavo Duarte) [1534949]
- [crypto] crypto/nx: Use percpu send window for NX requests (Gustavo Duarte) [1534949]
- [fs] debugfs: fix debugfs_real_fops() build error (Gustavo Duarte) [1533827]
- [fs] debugfs: defer debugfs_fsdata allocation to first usage (Gustavo Duarte) [1533827]
- [fs] debugfs: call debugfs_real_fops() only after debugfs_file_get() (Gustavo Duarte) [1533827]
- [fs] debugfs: purge obsolete SRCU based removal protection (Gustavo Duarte) [1533827]
- [infiniband] IB/hfi1: convert to debugfs_file_get() and -put() (Gustavo Duarte) [1533827]
- [fs] debugfs: convert to debugfs_file_get() and -put() (Gustavo Duarte) [1533827]
- [fs] debugfs: debugfs_real_fops(): drop __must_hold sparse annotation (Gustavo Duarte) [1533827]
- [fs] debugfs: implement per-file removal protection (Gustavo Duarte) [1533827]
- [fs] debugfs: add support for more elaborate ->d_fsdata (Gustavo Duarte) [1533827]
- [netdrv] cxgb4vf: Fix SGE FL buffer initialization logic for 64K pages (Arjun Vynipadath) [1533344]
- [redhat] spec: Add new arch/powerpc/kernel/module.lds file to kernel-devel rpm (Desnes Augusto Nunes do Rosario) [1466697]
- [powerpc] powerpc/modules: Fix alignment of .toc section in kernel modules (Desnes Augusto Nunes do Rosario) [1466697]

* Fri Jan 19 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-27.el7a]
- [acpi] ACPI / APEI: Remove arch_apei_flush_tlb_one() (Prarit Bhargava) [1513713]
- [arm64] mm: Remove arch_apei_flush_tlb_one() (Prarit Bhargava) [1513713]
- [acpi] ACPI / APEI: Remove ghes_ioremap_area (Prarit Bhargava) [1513713]
- [acpi] ACPI / APEI: Replace ioremap_page_range() with fixmap (Prarit Bhargava) [1513713]
- [misc] cxl: Add support for POWER9 DD2 (Steve Best) [1534959]
- [netdrv] ibmvnic: Fix pending MAC address changes (Steve Best) [1535360]
- [cpufreq] powernv: Dont assume distinct pstate values for nominal and pmin (Steve Best) [1534464]
- [netdrv] net: hns: add ACPI mode support for ethtool -p (Zhou Wang) [1530124]

* Thu Jan 18 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-26.el7a]
- [drm] uapi: fix linux/kfd_ioctl.h userspace compilation errors (Yaakov Selkowitz) [1510150]
- [net] uapi: fix linux/tls.h userspace compilation error (Yaakov Selkowitz) [1510150]
- [net] uapi: fix linux/rxrpc.h userspace compilation errors (Yaakov Selkowitz) [1510150]

* Tue Jan 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-25.el7a]
- [netdrv] ibmvnic: Don't handle RX interrupts when not up (Steve Best) [1532344]
- [redhat] configs: enable SELinux Infiniband access controls (Jonathan Toppins) [1524484]
- [infiniband] IB/mlx4: Fix RSS hash fields restrictions (Jonathan Toppins) [1524484]
- [infiniband] RDMA/netlink: Fix general protection fault (Jonathan Toppins) [1524484]
- [infiniband] IB/core: Bound check alternate path port number (Jonathan Toppins) [1524484]
- [infiniband] IB/core: Don't enforce PKey security on SMI MADs (Jonathan Toppins) [1524484]
- [infiniband] IB/core: Fix use workqueue without WQ_MEM_RECLAIM (Jonathan Toppins) [1524491]
- [infiniband] IB/core: Avoid crash on pkey enforcement failed in received MADs (Jonathan Toppins) [1524491]
- [infiniband] IB/srp: Avoid that a cable pull can trigger a kernel crash (Jonathan Toppins) [1524491]
- [infiniband] IB/cm: Fix memory corruption in handling CM request (Jonathan Toppins) [1524491]
- [infiniband] IB/srpt: Do not accept invalid initiator port names (Jonathan Toppins) [1524491]
- [infiniband] IB/core: Only enforce security for InfiniBand (Jonathan Toppins) [1523309]
- [infiniband] IB/core: Only maintain real QPs in the security lists (Jonathan Toppins) [1523309]
- [infiniband] IB/core: Avoid unnecessary return value check (Jonathan Toppins) [1523309]
- [misc] genwqe: Take R/W permissions into account when dealing with memory pages (Steve Best) [1528751]
- [arm64] Enable Qualcomm erratum 1041 workaround (Steve Ulrich) [1511024]
- [arm64] Add software workaround for Falkor erratum 1041 (Steve Ulrich) [1511024]
- [arm64] Define cputype macros for Falkor CPU (Steve Ulrich) [1511024]

* Mon Jan 15 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-24.el7a]
- [powerpc] KVM: PPC: Book3S HV: Always flush TLB in kvmppc_alloc_reset_hpt() (David Gibson) [1533315]
- [powerpc] pseries: Make RAS IRQ explicitly dependent on DLPAR WQ (David Gibson) [1517598]
- [tools] cpupower: Fix no-rounding MHz frequency output (Prarit Bhargava) [1503286]
- [x86] perf/x86/intel: Hide TSX events when RTM is not supported (Jiri Olsa) [1510552]
- [tools] perf test: Disable test cases 19 and 20 on s390x (Jiri Olsa) [1432652]
- [infiniband] iw_cxgb4: only clear the ARMED bit if a notification is needed (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: atomically flush the qp (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: only call the cq comp_handler when the cq is armed (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: Fix possible circular dependency locking warning (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: remove BUG_ON() usage (Arjun Vynipadath) [1458305]
- [infiniband] RDMA/cxgb4: Protect from possible dereference (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: add referencing to wait objects (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each ep object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each qp object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each cq object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each memory object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: change pr_debug to appropriate log level (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: Remove __func__ parameter from pr_debug() (Arjun Vynipadath) [1458305]
- [mm] kernel: mm/pagewalk.c: walk_hugetlb_range function mishandles holes in hugetlb ranges causing information leak (Chris von Recklinghausen) [1520395] {CVE-2017-16994}
- [redhat] Disable CONFIG_RC_CORE for s390x and aarch64 ("Herton R. Krzesinski") [1516037]

* Thu Jan 11 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-23.el7a]
- [s390] KVM: s390: Fix skey emulation permission check (Thomas Huth) [1530594]
- [scsi] core: check for device state in __scsi_remove_target() (Ewan Milne) [1513029]
- [virtio] virtio_mmio: fix devm cleanup (Andrew Jones) [1529279]
- [virtio] ptr_ring: add barriers (Andrew Jones) [1529279]
- [tools] virtio: ptr_ring: fix up after recent ptr_ring changes (Andrew Jones) [1529279]
- [netdrv] virtio_net: fix return value check in receive_mergeable() (Andrew Jones) [1529279]
- [virtio] virtio_mmio: add cleanup for virtio_mmio_remove (Andrew Jones) [1529279]
- [virtio] virtio_mmio: add cleanup for virtio_mmio_probe (Andrew Jones) [1529279]
- [netdrv] tap: free skb if flags error (Andrew Jones) [1529279]
- [netdrv] tun: free skb in early errors (Andrew Jones) [1529279]
- [vhost] net: fix skb leak in handle_rx() (Andrew Jones) [1529279]
- [virtio] virtio: release virtio index when fail to device_register (Andrew Jones) [1529279]
- [nvme] call blk_integrity_unregister after queue is cleaned up (Ming Lei) [1521000]
- [redhat] configs: Disable CONFIG_CMA and CONFIG_DMA_CMA support for RHEL archs (Bhupesh Sharma) [1519317]
- [redhat] configs: disable bnx2* storage offload drivers on aarch64 (Michal Schmidt) [1500020]
- [redhat] configs: Enable Qualcomm L2&L3 PMU drivers (Steve Ulrich) [1268469]
- [perf] qcom_l2_pmu: add event names (Steve Ulrich) [1268469]
- [i2c] xgene-slimpro: Support v2 (Iyappan Subramanian) [1524732]
- [hwmon] xgene: Minor clean up of ifdef and acpi_match_table reference (Iyappan Subramanian) [1524732]
- [hwmon] xgene: Support hwmon v2 (Iyappan Subramanian) [1524732]
- [net] Fix double free and memory corruption in get_net_ns_by_id() (Aristeu Rozanski) [1531553] {CVE-2017-15129}

* Tue Jan 09 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-22.el7a]
- [arm64] kaslr: Put kernel vectors address in separate data page (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Introduce TTBR_ASID_MASK for getting at the ASID in the TTBR (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] Kconfig: Add CONFIG_UNMAP_KERNEL_AT_EL0 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Add fake CPU feature for unmapping the kernel at EL0 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] tls: Avoid unconditional zeroing of tpidrro_el0 for native tasks (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] erratum: Work around Falkor erratum #E1003 in trampoline code (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Hook up entry trampoline to exception vectors (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Explicitly pass exception level to kernel_ventry macro (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Map entry trampoline into trampoline and kernel page tables (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Add exception trampoline page for exceptions from EL0 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Invalidate both kernel and user ASIDs when performing TLBI (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Add arm64_kernel_unmapped_at_el0 helper (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Allocate ASIDs in pairs (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Fix and re-enable ARM64_SW_TTBR0_PAN (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Rename post_ttbr0_update_workaround (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Remove pre_ttbr0_update_workaround for Falkor erratum #E1003 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Move ASID from TTBR0 to TTBR1 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Temporarily disable ARM64_SW_TTBR0_PAN (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Use non-global mappings for kernel space (Mark Salter) [1531357] {CVE-2017-5754}

* Mon Jan 08 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-21.el7a]
- [netdrv] bnx2x: Improve reliability in case of nested PCI errors (Steve Best) [1529861]
- [netdrv] tg3: Fix rx hang on MTU change with 5717/5719 (Mauricio Oliveira) [1526319]
- [target] cxgbit: Abort the TCP connection in case of data out timeout (Arjun Vynipadath) [1458313]
- [scsi] csiostor: enable PCIe relaxed ordering if supported (Arjun Vynipadath) [1458319]
- [crypto] chcr: Replace _manual_ swap with swap macro (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Fix memory leak (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Move DMA un/mapping to chcr from lld cxgb4 driver (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Remove allocation of sg list to implement 2K limit of dsgl header (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Use x8_ble gf multiplication to calculate IV (Arjun Vynipadath) [1458316]
- [crypto] gf128mul: The x8_ble multiplication functions (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Check error code with IS_ERR macro (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Remove unused parameter (Arjun Vynipadath) [1458316]
- [crypto] chelsio: pr_err() strings should end with newlines (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Use GCM IV size constant (Arjun Vynipadath) [1458316]
- [crypto] gcm: add GCM IV size constant (Arjun Vynipadath) [1458316]
- [scsi] libcxgbi: simplify task->hdr allocation for mgmt cmds (Arjun Vynipadath) [1458308]
- [scsi] cxgb4i: fix Tx skb leak (Arjun Vynipadath) [1458308]
- [scsi] libcxgbi: in case of vlan pass 0 as ifindex to find route (Arjun Vynipadath) [1458308]
- [scsi] libcxgbi: remove redundant check and close on csk (Arjun Vynipadath) [1458308]

* Fri Jan 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-20.el7a]
- [netdrv] igb: Use smp_rmb rather than read_barrier_depends (Steve Best) [1531097]
- [netdrv] ibmvnic: Include header descriptor support for ARP packets (Steve Best) [1529747]
- [netdrv] ibmvnic: Increase maximum number of RX/TX queues (Steve Best) [1529747]
- [netdrv] ibmvnic: Rename IBMVNIC_MAX_TX_QUEUES to IBMVNIC_MAX_QUEUES (Steve Best) [1529747]
- [powerpc] KVM: PPC: Book3S HV: Fix pending_pri value in kvmppc_xive_get_icp() (Laurent Vivier) [1524884]
- [powerpc] KVM: PPC: Book3S: fix XIVE migration of pending interrupts (Laurent Vivier) [1493453]
- [fs] cifs: fix NULL deref in SMB2_read (Leif Sahlberg) [1524797]
- [powerpc] perf: Dereference BHRB entries safely (Steve Best) [1525101]
- [tools] perf tests attr: Fix group stat tests (Jiri Olsa) [1518232]
- [tools] perf test attr: Fix ignored test case result (Jiri Olsa) [1518232]
- [tools] perf test attr: Fix python error on empty result (Jiri Olsa) [1518232]
- [tools] perf tests attr: Make hw events optional (Jiri Olsa) [1518232]
- [tools] perf tests attr: Fix task term values (Jiri Olsa) [1518232]
- [powerpc] kvm: ppc: book3s hv: Don't call real-mode XICS hypercall handlers if not enabled (Laurent Vivier) [1524664]
- [tools] perf vendor events: Use more flexible pattern matching for CPU identification for mapfile.csv (Jiri Olsa) [1513805]
- [tools] perf pmu: Extract function to get JSON alias map (Jiri Olsa) [1513805]
- [tools] perf pmu: Add helper function is_pmu_core to detect PMU CORE devices (Jiri Olsa) [1513805]

* Thu Jan 04 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-19.el7a]
- [redhat] RHMAINTAINERS: Cleanup tabs/spaces (Jeremy Linton)
- [redhat] RHMAINTAINERS: claim orphan sky2 (Jeremy Linton)
- [redhat] RHMAINTAINERS: arch/arm64 is supported (Jeremy Linton)
- [redhat] RHMAINTAINERS: add ARM device IP drivers (Jeremy Linton)
- [powerpc] powerpc/64s/slice: Use addr limit when computing slice mask (Steve Best) [1523265]
- [powerpc] powerpc/64s: mm_context.addr_limit is only used on hash (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Allow MAP_FIXED allocations to cross 128TB boundary (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Fix 128TB-512TB virtual address boundary case allocation (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Fix fork() with 512TB process address space (Steve Best) [1523265]
- [powerpc] powerpc/64s/radix: Fix 128TB-512TB virtual address boundary case allocation (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Fix 512T hint detection to use >= 128T (Steve Best) [1523265]

* Fri Dec 08 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-18.el7a]
- [powerpc] powerpc/64s: Initialize ISAv3 MMU registers before setting partition table (Steve Best) [1523226]
- [powerpc] KVM: PPC: Book3S HV: Fix use after free in case of multiple resize requests (Serhii Popovych) [1519046]
- [powerpc] KVM: PPC: Book3S HV: Drop prepare_done from struct kvm_resize_hpt (Serhii Popovych) [1519046]
- [netdrv] net: thunderx: Fix TCP/UDP checksum offload for IPv4 pkts (Florian Westphal) [1518375]
- [netdrv] cxgb4vf: define get_fecparam ethtool callback (Arjun Vynipadath) [1458300]
- [netdrv] cxgb4vf: make a couple of functions static (Arjun Vynipadath) [1458300]
- [virt] KVM: arm/arm64: vgic-v4: Only perform an unmap for valid vLPIs (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic-its: Check result of allocation before use (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic-its: Preserve the revious read from the pending table (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic: Preserve the revious read from the pending table (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic-irqfd: Fix MSI entry allocation (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: VGIC: extend !vgic_is_initialized guard (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: Don't queue VLPIs on INV/INVALL (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: Fix GICv4 ITS initialization issues (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Theory of operations (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Enable VLPI support (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Prevent userspace from changing doorbell affinity (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Prevent a VM using GICv4 from being saved (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Enable virtual cpuif if VLPIs can be delivered (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Hook vPE scheduling into vgic flush/sync (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Use the doorbell interrupt as an unblocking source (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Add doorbell interrupt handling (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Use pending_last as a scheduling hint (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle INVALL applied to a vPE (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Propagate property updates to VLPIs (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle MOVALL applied to a vPE (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle CLEAR applied to a VLPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Propagate affinity changes to the physical ITS (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Unmap VLPI when freeing an LPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle INT command applied to a VLPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Wire mapping/unmapping of VLPIs in VFIO irq bypass (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Add init/teardown of the per-VM vPE irq domain (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Add property field and per-VM predicate (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: vITS: Add a helper to update the affinity of an LPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: vITS: Add MSI translation helpers (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Fix VPE activate callback return value (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: vgic: restructure kvm_vgic_(un)map_phys_irq (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: register irq bypass consumer on ARM/ARM64 (Auger Eric) [1386368]
- [irqchip] KVM: arm/arm64: Check that system supports split eoi/deactivate (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: Support calling vgic_update_irq_pending from irq context (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: Guard kvm_vgic_map_is_active against !vgic_initialized (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3: pr_err() strings should end with newlines (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3: Fix ppi-partitions lookup (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v4: Clear IRQ_DISABLE_UNLAZY again if mapping fails (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Setup VLPI properties at map time (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Update effective affinity on VPE mapping (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Only send VINVALL to a single ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Limit scope of VPE mapping to be per ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Make its_send_vmapp operate on a single ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Make its_send_vinvall operate on a single ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Make GICv4_ITS_LIST_MAX globally available (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Track per-ITS list number (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Pass its_node pointer to each command builder (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Add post-mortem info on command timeout (Auger Eric) [1386368]
- [irqchip] irqchip/gic: Make quirks matching conditional on init return value (Auger Eric) [1386368]
- [kernel] genirq/irqdomain: Update irq_domain_ops.activate() signature (Auger Eric) [1386368]
- [net] openvswitch: datapath: fix data type in queue_gso_packets (Davide Caratti) [1519190]
- [net] accept UFO datagrams from tuntap and packet (Davide Caratti) [1519190]
- [net] Remove unused skb_shared_info member (Davide Caratti) [1519190]
- [redhat] configs: Enable CONFIG_VIRTIO_BLK_SCSI (Fam Zheng) [1487183]

* Fri Dec 08 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-17.el7a]
- [mm] kernel: pmd can become dirty without going through a COW cycle (Chris von Recklinghausen) [1518612] {CVE-2017-1000405}
- [powerpc] powerpc/perf: Fix oops when grouping different pmu events (Steve Best) [1520838]
- [net] sctp: use right member as the param of list_for_each_entry (Xin Long) [1520264]
- [netdrv] cxgb4: add new T6 pci device id's (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: add new T5 pci device id's (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: add new T6 pci device id's (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: do DCB state reset in couple of places (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: avoid stall while shutting down the adapter (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: add new T5 pci device id's (Arjun Vynipadath) [1458297]
- [powerpc] Revert powerpc: Do not call ppc_md.panic in fadump panic notifier (David Gibson) [1513858]
- [arm64] KVM: fix VTTBR_BADDR_MASK BUG_ON off-by-one (Andrew Jones) [1520938]
- [firmware] Revert efi/arm: Don't mark ACPI reclaim memory as MEMBLOCK_NOMAP (Bhupesh Sharma) [1512379]
- [gpio] dwapb: Add wakeup source support (Iyappan Subramanian) [1497813]
- [redhat] configs: zram, ppc64: enable zram on ppc64 (Jerome Marchand) [1499197]
- [redhat] configs: Enable MMC DesignWare (Slava Shwartsman) [1477045]

* Thu Dec 07 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-16.el7a]
- [powerpc] Do not assign thread.tidr if already assigned (Gustavo Duarte) [1320916]
- [powerpc] Avoid signed to unsigned conversion in set_thread_tidr() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Export chip_to_vas_id() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Add support for user receive window (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Define vas_win_id() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Define vas_win_paste_addr() (Gustavo Duarte) [1320916]
- [powerpc] Define set_thread_uses_vas() (Gustavo Duarte) [1320916]
- [powerpc] Add support for setting SPRN_TIDR (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Export HVWC to debugfs (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas, nx-842: Define and use chip_to_vas_id() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Create cpu to vas id mapping (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: poll for return of window credits (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Save configured window credits (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Reduce polling interval for busy state (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Use helper to unpin/close window (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Drop poll_window_cast_out() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Cleanup some debug code (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Validate window credits (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: init missing fields from rxattr/txattr (Gustavo Duarte) [1320916]
- [vfio] vfio/type1: silence integer overflow warning (Auger Eric) [1515981]
- [vfio] vfio/pci: Virtualize Maximum Read Request Size (Auger Eric) [1515981]
- [kernel] sysctl: check for UINT_MAX before unsigned int min/max (Joe Lawrence) [1499478]
- [fs] pipe: add proc_dopipe_max_size() to safely assign pipe_max_size (Joe Lawrence) [1499478]
- [fs] pipe: avoid round_pipe_size() nr_pages overflow on 32-bit (Joe Lawrence) [1499478]
- [fs] pipe: match pipe_max_size data type with procfs (Joe Lawrence) [1499478]
- [iommu] iommu/iova: Make rcache flush optional on IOVA allocation failure (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Don't try to copy anchor nodes (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Try harder to allocate from rcache magazine (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Make rcache limit_pfn handling more robust (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Simplify domain destruction (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Simplify cached node logic (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Add rbtree anchor node (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Make dma_32bit_pfn implicit (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Extend rbtree node caching (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Optimise the padding calculation (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Optimise rbtree searching (Steve Ulrich) [1514191]
- [powerpc] powerpc/kexec: Fix kexec/kdump in P9 guest kernels (David Gibson) [1513905]
- [powerpc] KVM: PPC: Book3S HV: Fix migration and HPT resizing of HPT guests on radix hosts (Suraj Jitindar Singh) [1517052]

* Tue Dec 05 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-15.el7a]
- [virtio] virtio_balloon: fix increment of vb->num_pfns in fill_balloon() (Andrew Jones) [1516486]
- [redhat] RHMAINTAINERS: add vfio sections (Andrew Jones)
- [redhat] RHMAINTAINERS: update virtio sections (Andrew Jones)
- [redhat] RHMAINTAINERS: update KVM sections (Andrew Jones)
- [net] ip6_tunnel: clean up ip4ip6 and ip6ip6's err_handlers (Xin Long) [1510242]
- [net] ip6_tunnel: process toobig in a better way (Xin Long) [1510242]
- [net] ip6_tunnel: add the process for redirect in ip6_tnl_err (Xin Long) [1510242]
- [net] ip6_gre: process toobig in a better way (Xin Long) [1509915]
- [net] ip6_gre: add the process for redirect in ip6gre_err (Xin Long) [1509915]
- [net] route: also update fnhe_genid when updating a route cache (Xin Long) [1509098]
- [net] route: update fnhe_expires for redirect when the fnhe exists (Xin Long) [1509098]
- [net] ip_gre: add the support for i/o_flags update via ioctl (Xin Long) [1489338]
- [net] ip_gre: add the support for i/o_flags update via netlink (Xin Long) [1489338]

* Tue Dec 05 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-14.el7a]
- [block] drain queue before waiting for q_usage_counter becoming zero (Ming Lei) [1513036]
- [block] wake up all tasks blocked in get_request() (Ming Lei) [1513036]
- [block] Make q_usage_counter also track legacy requests (Ming Lei) [1513036]

* Tue Dec 05 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-13.el7a]
- [redhat] configs: disable ATA on s390x ("Herton R. Krzesinski") [1514589]
- [iommu] Print a message with the default domain type created (Al Stone) [1518977]
- [iommu] aarch64: Set bypass mode per default (Al Stone) [1518977]
- [tools] perf bench numa: Fixup discontiguous/sparse numa nodes (Steve Best) [1516472]

* Mon Dec 04 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-12.el7a]
- [powerpc] KVM: PPC: Book3S HV: Cosmetic post-merge cleanups (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Run HPT guests on POWER9 radix hosts (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Allow for running POWER9 host in single-threaded mode (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Add infrastructure for running HPT guests on radix host (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Unify dirty page map between HPT and radix (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Rename hpte_setup_done to mmu_ready (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Don't rely on host's page size information (Suraj Jitindar Singh) [1485099]
- [powerpc] Revert KVM: PPC: Book3S HV: POWER9 does not require secondary thread management (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Explicitly disable HPT operations on radix guests (Suraj Jitindar Singh) [1485099]

* Fri Dec 01 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-11.el7a]
- [powerpc] powerpc/mce: hookup memory_failure for UE errors (Steve Best) [1517693]
- [powerpc] powerpc/mce: Hookup ierror (instruction) UE errors (Steve Best) [1517693]
- [powerpc] powerpc/mce: Hookup derror (load/store) UE errors (Steve Best) [1517693]
- [powerpc] powerpc/mce: Align the print of physical address better (Steve Best) [1517693]
- [powerpc] powerpc/mce: Remove unused function get_mce_fault_addr() (Steve Best) [1517693]
- [virtio] virtio_balloon: fix deadlock on OOM (Andrew Jones) [1516486]

* Thu Nov 30 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-10.el7a]
- [block] bio: ensure __bio_clone_fast copies bi_partno (Ming Lei) [1516243]
- [net] icmp: don't fail on fragment reassembly time exceeded (Matteo Croce) [1495458]
- [netdrv] geneve: only configure or fill UDP_ZERO_CSUM6_RX/TX info when CONFIG_IPV6 (Hangbin Liu) [1511839]
- [netdrv] geneve: fix fill_info when link down (Hangbin Liu) [1511839]
- [redhat] allow specifying BUILDID on the command line (Andrew Jones)
- [redhat] also ignore .old config files (Andrew Jones)
- [redhat] stop leaving empty temp files (Andrew Jones)

* Wed Nov 29 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-9.el7a]
- [netdrv] i40e: Use smp_rmb rather than read_barrier_depends (Mauricio Oliveira) [1513182]
- [netdrv] ixgbe: Fix skb list corruption on Power systems (Mauricio Oliveira) [1513182]

* Wed Nov 29 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-8.el7a]
- [netdrv] ibmvnic: fix dma_mapping_error call (Steve Best) [1515330]
- [netdrv] ibmvnic: Feature implementation of Vital Product Data (VPD) for the ibmvnic driver (Steve Best) [1515330]
- [netdrv] ibmvnic: Add vnic client data to login buffer (Steve Best) [1515330]
- Revert "[block] Make q_usage_counter also track legacy requests" ("Herton R. Krzesinski")
- Revert "[block] wake up all tasks blocked in get_request()" ("Herton R. Krzesinski")
- Revert "[block] run queue before waiting for q_usage_counter becoming zero" ("Herton R. Krzesinski")
- Revert "[block] drain blkcg part of request_queue in blk_cleanup_queue()" ("Herton R. Krzesinski")

* Tue Nov 28 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-7.el7a]
- [block] drain blkcg part of request_queue in blk_cleanup_queue() (Ming Lei) [1513036]
- [block] run queue before waiting for q_usage_counter becoming zero (Ming Lei) [1513036]
- [block] wake up all tasks blocked in get_request() (Ming Lei) [1513036]
- [block] Make q_usage_counter also track legacy requests (Ming Lei) [1513036]

* Tue Nov 28 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-6.el7a]
- [tools] perf vendor events powerpc: Update POWER9 events (Steve Best) [1509681]

* Mon Nov 27 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-5.el7a]
- [pci] Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Torez Smith) [1508505 1513168]
- [iommu] arm-smmu, acpi: Enable Cavium SMMU-v3 (Torez Smith) [1508505 1513168]
- [iommu] arm-smmu, acpi: Enable Cavium SMMU-v2 (Torez Smith) [1508505 1513168]
- [netdrv] net: thunderx: Fix TCP/UDP checksum offload for IPv6 pkts (Florian Westphal) [1511683]
- [net] ipv6: Fixup device for anycast routes during copy (Florian Westphal) [1508339]

* Wed Nov 22 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-4.el7a]
- [powerpc] revert powerpc/powernv/cpufreq: Fix the frequency read by /proc/cpuinfo (Steve Best) [1514611]

* Tue Nov 21 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-3.el7a]
- [cpufreq] stats: Handle the case when trans_table goes beyond PAGE_SIZE (Desnes Augusto Nunes do Rosario) [1499411]
- [virt] KVM: arm/arm64: vgic-its: Implement KVM_DEV_ARM_ITS_CTRL_RESET (Auger Eric) [1490315]
- [documentation] KVM: arm/arm64: Document KVM_DEV_ARM_ITS_CTRL_RESET (Auger Eric) [1490315]
- [virt] KVM: arm/arm64: vgic-its: Free caches when GITS_BASER Valid bit is cleared (Auger Eric) [1490315]
- [virt] KVM: arm/arm64: vgic-its: New helper functions to free the caches (Auger Eric) [1490315]
- [virt] KVM: arm/arm64: vgic-its: Remove kvm_its_unmap_device (Auger Eric) [1490315]
- [tools] cpupower : Fix cpupower working when cpu0 is offline (Steve Best) [1495559]
- [scsi] scsi_sysfs: make unpriv_sgio queue attribute accessible for non-block devices (Paolo Bonzini) [1492769]
- [block] sg_io: introduce unpriv_sgio queue flag (Paolo Bonzini) [1492769]
- [block] sg_io: pass request_queue to blk_verify_command (Paolo Bonzini) [1492769]
- [kernel] locking/qrwlock: Prevent slowpath writers getting held up by fastpath (Waiman Long) [1507568]
- [arm64] locking/qrwlock, arm64: Move rwlock implementation over to qrwlocks (Waiman Long) [1507568]
- [kernel] locking/qrwlock: Use atomic_cond_read_acquire() when spinning in qrwlock (Waiman Long) [1507568]
- [kernel] locking/atomic: Add atomic_cond_read_acquire() (Waiman Long) [1507568]
- [kernel] locking/qrwlock: Use 'struct qrwlock' instead of 'struct __qrwlock' (Waiman Long) [1507568]

* Fri Nov 17 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-2.el7a]
- [powerpc] powerpc/powernv/cpufreq: Fix the frequency read by /proc/cpuinfo (Steve Best) [1501944]
- [netdrv] ibmvnic: Set state UP (Steve Best) [1512272]
- [powerpc] powerpc/64s: Add workaround for P9 vector CI load issue (Steve Best) [1501403]

* Mon Nov 13 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-1.el7a]
- [redhat] kernel-alt rebased to 4.14 ("Herton R. Krzesinski") [1492717]
- [scsi] cxlflash: Derive pid through accessors (Steve Best) [1510168]
- [scsi] cxlflash: Allow cards without WWPN VPD to configure (Steve Best) [1510168]
- [scsi] cxlflash: Use derived maximum write same length (Steve Best) [1510168]
- [redhat] configs: Enable hardlockup detector for powerpc64le (Bhupesh Sharma) [1478225]
- [redhat] configs: Enable softlockup detector by default (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/powernv: Implement NMI IPI with OPAL_SIGNAL_SYSTEM_RESET (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/xmon: Avoid tripping SMP hardlockup watchdog (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/watchdog: Do not trigger SMP crash from touch_nmi_watchdog (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/watchdog: Do not backtrace locked CPUs twice if allcpus backtrace is enabled (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/watchdog: Do not panic from locked CPU's IPI handler (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/64s: Implement system reset idle wakeup reason (Bhupesh Sharma) [1478225]
- [misc] cxl: Enable global TLBIs for cxl contexts (Gustavo Duarte) [1498927]
- [powerpc] powerpc/mm: Export flush_all_mm() (Gustavo Duarte) [1498927]
- [misc] cxl: Set the valid bit in PE for dedicated mode (Gustavo Duarte) [1498927]
- [kernel] kdump: support crashkernel=auto for compatibility (Pingfan Liu) [1431982]
- [kernel] kdump/parse_crashkernel_mem: round up the total memory size to 128M (Dave Young) [1431982]
- [x86] x86/kdump: crashkernel=X try to reserve below 896M first then below 4G and MAXMEM (Dave Young) [1431982]
- [netdrv] ibmvnic: Fix failover error path for non-fatal resets (Steve Best) [1464528]
- [netdrv] ibmvnic: Update reset infrastructure to support tunable parameters (Steve Best) [1464528]
- [netdrv] ibmvnic: Let users change net device features (Steve Best) [1464528]
- [netdrv] ibmvnic: Enable TSO support (Steve Best) [1464528]
- [netdrv] ibmvnic: Enable scatter-gather support (Steve Best) [1464528]
- [powerpc] KVM: PPC: Tie KVM_CAP_PPC_HTM to the user-visible TM feature (Steve Best) [1498555]
- [powerpc] powerpc/tm: P9 disable transactionally suspended sigcontexts (Steve Best) [1498555]
- [powerpc] powerpc/powernv: Enable TM without suspend if possible (Steve Best) [1498555]
- [powerpc] Add PPC_FEATURE2_HTM_NO_SUSPEND (Steve Best) [1498555]
- [powerpc] powerpc/tm: Add commandline option to disable hardware transactional memory (Steve Best) [1498555]
- [arm64] DO NOT UPSTREAM - topology: Adjust sysfs topology (Andrew Jones) [1501443]
- [arm64] DO NOT UPSTREAM - pmuv3: disable PMUv3 in VM when vPMU=off (Andrew Jones) [1501452]
- [redhat] configs: s390: Enable CONFIG_FTRACE_SYSCALLS option (Jiri Olsa) [1469687]
- [redhat] configs: s390x: Disable CONFIG_S390_GUEST_OLD_TRANSPORT (David Hildenbrand) [1495197]
- [redhat] configs: enable CONFIG_MEM_SOFT_DIRTY on ppc64le (Adrian Reber) [1496347]
- [redhat] configs: enable CHECKPOINT_RESTORE on s390x (Adrian Reber) [1457968]
- [redhat] remove usage of mandocs target for kernel-doc, avoid running htmldocs ("Herton R. Krzesinski")


###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
