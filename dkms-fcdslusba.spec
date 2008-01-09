%define module fcdslusba
%define version 3.11.05
%define card "AVM GmbH|FtitzCard USB DSL SL USB"

Summary: dkms package for %{module} driver
Name: dkms-%{module}
Version: %{version}
Release: %mkrel 6
Source0: ftp://ftp.avm.de/cardware/fritzcrd.dsl_usb_analog/linux/suse.93/fcdslusba-suse93-3.11-05.tar.bz2
Source1: dkms-fcdslusba-use-autoconf-header.patch
Source2: dkms-fcdslusba-dont-redefine-uintptr_t.patch
Source3: dkms-fcdslusba-remove-usb_driver_owner.patch
Source4: dkms-fcdslusba-remove-DECLARE_MUTEX_LOCKED.patch
Source5: dkms-fcdslusba-update-INIT_WORK-changes.patch
Source6: dkms-fcdslusba-update-usb_complete_t-functions.patch
Patch0: fritz-xchg.patch
License: Commercial
Group: System/Kernel and hardware
URL: http://www.avm.de/
Requires(post): dkms
Requires(preun): dkms
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildArch: noarch

%description
This package contains the %{module} driver for %{card}

%prep
%setup -n fritz/src -q
%patch0 -p2
# copy the lib in the source tree, do not use some obscure place like /var/lib/fritz
cp ../lib/*.o .
# do not try to copy the lib in LIBDIR
perl -pi -e 's!.*cp -f \.\./lib.*!!' Makefile
# fool Makefile by using a already existing LIBDIR
perl -pi -e 's!(LIBDIR.*):=.*!$1:= \$(SUBDIRS)!' Makefile
#- dkms pass KERNELRELEASE and confuse the Makefile, rely on KERNELVERSION instead
perl -pi -e 's!(ifneq.*)KERNELRELEASE!$1KERNELVERSION!' Makefile
#- build for kernel release dkms is asking for
perl -pi -e 's!shell uname -r!KERNELRELEASE!' Makefile

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/src/%module-%version-%release/patches
cat > $RPM_BUILD_ROOT/usr/src/%module-%version-%release/dkms.conf <<EOF
PACKAGE_NAME=%module
PACKAGE_VERSION=%version-%release

DEST_MODULE_LOCATION[0]=/kernel/drivers/isdn/capi
BUILT_MODULE_NAME[0]=%module
MAKE[0]="make"
CLEAN="make clean"
AUTOINSTALL="yes"
PATCH[0]="dkms-fcdslusba-use-autoconf-header.patch"
PATCH_MATCH[0]="^2\.6\.(19)|([2-9][0-9]+)|([1-9][0-9][0-9]+)"
PATCH[1]="dkms-fcdslusba-dont-redefine-uintptr_t.patch"
PATCH_MATCH[1]="^2\.6\.(2[4-9])|([3-9][0-9]+)|([1-9][0-9][0-9]+)"
PATCH[2]="dkms-fcdslusba-remove-usb_driver_owner.patch"
PATCH_MATCH[2]="^2\.6\.(1[6-9])|([2-9][0-9]+)|([1-9][0-9][0-9]+)"
PATCH[3]="dkms-fcdslusba-remove-DECLARE_MUTEX_LOCKED.patch"
PATCH_MATCH[3]="^2\.6\.(2[4-9])|([3-9][0-9]+)|([1-9][0-9][0-9]+)"
PATCH[4]="dkms-fcdslusba-update-INIT_WORK-changes.patch"
PATCH_MATCH[4]="^2\.6\.([2-9][0-9]+)|([1-9][0-9][0-9]+)"
PATCH[5]="dkms-fcdslusba-update-usb_complete_t-functions.patch"
PATCH_MATCH[5]="^2\.6\.(19)|([2-9][0-9]+)|([1-9][0-9][0-9]+)"
EOF

tar c . | tar x -C $RPM_BUILD_ROOT/usr/src/%module-%version-%release/

for p in %{_sourcedir}/dkms-fcdslusba-use-autoconf-header.patch \
         %{_sourcedir}/dkms-fcdslusba-dont-redefine-uintptr_t.patch \
         %{_sourcedir}/dkms-fcdslusba-remove-usb_driver_owner.patch \
         %{_sourcedir}/dkms-fcdslusba-remove-DECLARE_MUTEX_LOCKED.patch \
         %{_sourcedir}/dkms-fcdslusba-update-INIT_WORK-changes.patch \
         %{_sourcedir}/dkms-fcdslusba-update-usb_complete_t-functions.patch;
do
	cp $p $RPM_BUILD_ROOT/usr/src/%module-%version-%release/patches
done

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644,root,root,0755)
/usr/src/%module-%version-%release/

%post
/usr/sbin/dkms --rpm_safe_upgrade add -m %module -v %version-%release
/usr/sbin/dkms --rpm_safe_upgrade build -m %module -v %version-%release
/usr/sbin/dkms --rpm_safe_upgrade install -m %module -v %version-%release
exit 0

%preun
/usr/sbin/dkms --rpm_safe_upgrade remove -m %module -v %version-%release --all
exit 0

