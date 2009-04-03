%define _disable_ld_no_undefined 1

# configure options
%define with_snmp	0
%define	with_vtysh	1
%define	with_ospf_te	1
%define	with_nssa	1
%define	with_opaque_lsa	1
%define	with_tcp_zebra	0
%define	with_vtysh	1
%define	with_pam	1
%define	with_ipv6	1
%define	with_ospfclient	1
%define	with_ospfapi	1
%define	with_irdp	1
%define with_rtadv	1
%define	with_isisd	1 
%define	with_multipath	64
%define	quagga_user	quagga
%define	vty_group	quaggavt

# path defines
%define	zeb_src		%{_builddir}/%{name}-%{version}
%define	zeb_rh_src	%{zeb_src}/redhat
%define	zeb_docs	%{zeb_src}/doc

%define major 0
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Routing daemon
Name:           quagga
Version:        0.99.11
Release:        %mkrel 1
License:	GPL
Group:		System/Servers
URL:		http://www.quagga.net
Source0:	http://www.quagga.net/download/%{name}-%{version}.tar.gz
Source1:	http://www.quagga.net/download/%{name}-%{version}.tar.gz.asc
Patch0:         quagga-0.99.11-netlink.patch
Patch1:		quagga-0.96.5-nostart.patch
Patch2:		quagga-0.98.2-gcc4.patch
Patch3:		quagga-0.99.10-libcap.diff
Patch4:		quagga-0.99.11-fix-str-fmt.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	texinfo
BuildRequires:	tetex-texi2html
BuildRequires:	tetex
BuildRequires:	pam-devel
BuildRequires:	libpcap-devel
BuildRequires:	chrpath >= 0.12
BuildRequires:	automake1.7
BuildRequires:	autoconf2.5
%if %{with_snmp}
Requires:	net-snmp-mibs
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel
%endif
%if %{with_vtysh}
BuildRequires:	readline readline-devel ncurses ncurses-devel
Requires:		readline ncurses
%endif
# Initscripts > 5.60 is required for IPv6 support
Requires(pre):		initscripts >= 5.60
Requires:		initscripts >= 5.60
Requires(pre):		ncurses readline pam
Requires:		ncurses readline pam
Requires(preun):		info-install
Requires(post):		info-install
Provides:	routingdaemon
Obsoletes:	bird gated mrt zebra
Provides:	bird gated mrt zebra
Requires:	%{libname} = %{version}
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
Quagga is a free software that manages TCP/IP based routing
protocol. It takes multi-server and multi-thread approach to resolve
the current complexity of the Internet.

Quagga supports BGP4, BGP4+, OSPFv2, OSPFv3, RIPv1, RIPv2, and RIPng.

Quagga is intended to be used as a Route Server and a Route Reflector. It is
not a toolkit, it provides full routing power under a new architecture.
Quagga by design has a process for each protocol.

Quagga is a fork of GNU Zebra.

%package	contrib
Summary:	Tools for quagga
Group:		System/Servers

%description	contrib
Contributed/3rd party tools which may be of use with quagga.

%package -n	%{libname}
Summary:	Shared %{name} library
Group:          System/Libraries

%description -n	%{libname}
This package provides the shared %{name} library.

%package -n	%{develname}
Summary:	Header and object files for quagga development
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}
Provides:	lib%{name}-devel = %{version}
Obsoletes:	%{mklibname quagga 0 -d}

%description -n	%{develname}
The quagga-devel package contains the header and object files necessary for
developing OSPF-API and quagga applications.

%prep
%setup  -q
%patch0 -p1 -b .netlink
%patch1 -p1 -b .nostart
%patch2 -p1 -b .gcc4
%patch3 -p0 -b .libcap
%patch4 -p0 -b .str

%build
export CFLAGS="%{optflags} -fPIC"

%serverbuild
autoreconf -fi
%configure2_5x \
    --sysconfdir=%{_sysconfdir}/quagga \
    --localstatedir=/var/run/quagga \
%if %{with_ipv6}
    --enable-ipv6 \
%endif
%if %{with_snmp}
    --enable-snmp \
%endif
%if %{with_multipath}
    --enable-multipath=%{with_multipath} \
%endif
%if %{with_tcp_zebra}
    --enable-tcp-zebra \
%endif
%if %{with_nssa}
    --enable-nssa \
%endif
%if %{with_opaque_lsa}
    --enable-opaque-lsa \
%endif
%if %{with_ospf_te}
    --enable-ospf-te \
%endif
%if %{with_vtysh}
    --enable-vtysh \
%endif
%if %{with_ospfclient }
    --enable-ospfclient=yes \
%else
    --enable-ospfclient=no\
%endif
%if %{with_ospfapi}
    --enable-ospfapi=yes \
%else
    --enable-ospfapi=no \
%endif
%if %{with_irdp}
    --enable-irdp=yes \
%else
    --enable-irdp=no \
%endif
%if %{with_isisd}
    --enable-isisd \
%else
    --disable-isisd \
%endif
%if %{with_pam}
    --with-libpam \
%endif
%if %{quagga_user}
    --enable-user=%{quagga_user} \
    --enable-group=%{quagga_user} \
%endif
%if %{vty_group}
    --enable-vty-group=%{vty_group} \
%endif
%if %{with_rtadv}
    --with-rtadv \
%endif
    --with-cflags="%{optflags}" \
    --enable-netlink

make MAKEINFO="makeinfo --no-split"

pushd doc
    texi2html quagga.texi
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/pam.d
install -d %{buildroot}/var/log/quagga
install -d %{buildroot}/var/run/quagga
install -d %{buildroot}%{_infodir}

%makeinstall_std

# Remove this file, as it is uninstalled and causes errors when building on RH9
rm -rf %{buildroot}/usr/share/info/dir

install -m755 %{zeb_rh_src}/zebra.init %{buildroot}%{_initrddir}/zebra
install -m755 %{zeb_rh_src}/bgpd.init %{buildroot}%{_initrddir}/bgpd
%if %{with_ipv6}
install -m755 %{zeb_rh_src}/ospf6d.init %{buildroot}%{_initrddir}/ospf6d
install -m755 %{zeb_rh_src}/ripngd.init %{buildroot}%{_initrddir}/ripngd
%endif
install -m755 %{zeb_rh_src}/ospfd.init %{buildroot}%{_initrddir}/ospfd
install -m755 %{zeb_rh_src}/ripd.init %{buildroot}%{_initrddir}/ripd
install -m755 %{zeb_rh_src}/watchquagga.init %{buildroot}%{_initrddir}/watchquagga
%if %{with_isisd}
install -m755 %{zeb_rh_src}/isisd.init %{buildroot}%{_initrddir}/isisd
%endif
install -m644 %{zeb_rh_src}/quagga.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/quagga
install -m644 %{zeb_rh_src}/quagga.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/quagga

# fix conditional pam config file
%if %{mdkversion} < 200610
install -m644 %{zeb_rh_src}/quagga.pam.stack %{buildroot}%{_sysconfdir}/pam.d/quagga
%else
install -m644 %{zeb_rh_src}/quagga.pam %{buildroot}%{_sysconfdir}/pam.d/quagga
%endif

# nuke rpath
chrpath -d %{buildroot}%{_bindir}/*
chrpath -d %{buildroot}%{_sbindir}/*

%pre
# add vty_group
%if %{vty_group}
%_pre_groupadd %{vty_group}
%endif
# add quagga user and group
%if %{quagga_user}
%_pre_useradd %{quagga_user} %{_localstatedir}/lib /sbin/nologin
%endif

%post
%_post_service zebra
%_post_service ripd
%if %{with_ipv6}
%_post_service ospf6d
%_post_service ripngd
%endif
%_post_service ospfd
%_post_service bgpd
%_post_service watchquagga

%_install_info %{name}.info

# Create dummy files if they don't exist so basic functions can be used.
if [ ! -e %{_sysconfdir}/quagga/zebra.conf ]; then
	echo "hostname `hostname`" > %{_sysconfdir}/quagga/zebra.conf
%if %{quagga_user}
	chown %{quagga_user}:%{quagga_user} %{_sysconfdir}/quagga/zebra.conf
%endif
	chmod 640 %{_sysconfdir}/quagga/zebra.conf
fi
if [ ! -e %{_sysconfdir}/quagga/vtysh.conf ]; then
	touch %{_sysconfdir}/quagga/vtysh.conf
	chmod 640 %{_sysconfdir}/quagga/vtysh.conf
fi

%preun
%_preun_service zebra
%_preun_service ripd
%if %{with_ipv6}
%_preun_service ripngd
%endif
%_preun_service ospfd
%if %{with_ipv6}
%_preun_service ospf6d
%endif
%_preun_service bgpd
%_preun_service watchquagga

%_remove_install_info %{name}.info

%postun
%if %{quagga_user}
%_postun_userdel %{quagga_user}
%endif

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc */*.sample* AUTHORS COPYING doc/quagga.html doc/mpls
%doc ChangeLog INSTALL NEWS README REPORTING-BUGS SERVICES TODO
#
%if %{quagga_user}
%dir %attr(0751,%{quagga_user},%{quagga_user}) %{_sysconfdir}/quagga
%dir %attr(0750,%{quagga_user},%{quagga_user}) /var/log/quagga 
%dir %attr(0751,%{quagga_user},%{quagga_user}) /var/run/quagga
%else
#
%dir %attr(0750,root,root) %{_sysconfdir}/quagga
%dir %attr(0750,root,root) /var/log/quagga
%dir %attr(0750,root,root) /var/run/quagga
%endif
#
%if %{vty_group}
%attr(0640,%{quagga_user},%{vty_group}) %config(noreplace) %{_sysconfdir}/quagga/vtysh.conf*
%endif
#
%config(noreplace) %{_sysconfdir}/pam.d/quagga
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/quagga                  
%config(noreplace) %{_sysconfdir}/quagga/bgpd.conf*
%config(noreplace) %{_sysconfdir}/quagga/ospf6d.conf*
%config(noreplace) %{_sysconfdir}/quagga/ospfd.conf*
%config(noreplace) %{_sysconfdir}/quagga/ripd.conf*
%config(noreplace) %{_sysconfdir}/quagga/ripngd.conf*
%config(noreplace) %{_sysconfdir}/quagga/zebra.conf*
#
%attr(0755,root,root) %{_initrddir}/bgpd
%attr(0755,root,root) %{_initrddir}/ospf6d
%attr(0755,root,root) %{_initrddir}/ospfd
%attr(0755,root,root) %{_initrddir}/ripd
%attr(0755,root,root) %{_initrddir}/ripngd
%attr(0755,root,root) %{_initrddir}/watchquagga
%attr(0755,root,root) %{_initrddir}/zebra
#
%{_sbindir}/bgpd
%{_sbindir}/ospf6d
%{_sbindir}/ospfclient
%{_sbindir}/ospfd
%{_sbindir}/ripd
%{_sbindir}/ripngd
%{_sbindir}/watchquagga
%{_sbindir}/zebra
#
%if %{with_vtysh}
%{_bindir}/vtysh
%attr(0644,root,root) %{_mandir}/man1/vtysh.1*
%endif
#
%if %{with_isisd}
%attr(0755,root,root) %{_initrddir}/isisd
%config(noreplace) %{_sysconfdir}/quagga/isisd.conf*
%{_sbindir}/isisd
%attr(0644,root,root) %{_mandir}/man8/isisd.8*
%endif
#
%attr(0644,root,root) %{_mandir}/man8/bgpd.8*
%attr(0644,root,root) %{_mandir}/man8/ospf6d.8*
%attr(0644,root,root) %{_mandir}/man8/ospfd.8*
%attr(0644,root,root) %{_mandir}/man8/ripd.8*
%attr(0644,root,root) %{_mandir}/man8/ripngd.8*
%attr(0644,root,root) %{_mandir}/man8/zebra.8*
%{_infodir}/*info*

%files contrib
%defattr(-,root,root)
%doc tools

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%dir %{_includedir}/quagga
%{_includedir}/quagga/*.h
%dir %{_includedir}/quagga/ospfd/*
#
%if %{with_ospfapi}
%dir %{_includedir}/quagga/ospfapi/*
%endif
