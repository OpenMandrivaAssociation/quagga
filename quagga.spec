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
%define	with_pim	1
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
Version:        1.2.4
Release:        1
License:	GPL
Group:		System/Servers
URL:		https://www.nongnu.org/quagga/
Source0:	https://github.com/Quagga/quagga/releases/download/quagga-1.2.4/quagga-1.2.4.tar.gz
Patch0:         quagga-0.99.11-netlink.patch
Patch1:		quagga-1.2.4-fix-build-with-fcommon.patch
BuildRequires:	texinfo
BuildRequires:  texi2html
BuildRequires:  texlive
#BuildRequires:	tetex-texi2html
#BuildRequires:	tetex
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(libpcap)
BuildRequires:	chrpath >= 0.12
BuildRequires:	autoconf automake slibtool
%if %{with_snmp}
Requires:	net-snmp-mibs
BuildRequires:	net-snmp-devel
BuildRequires:	pkgconfig(openssl)
%endif
%if %{with_vtysh}
BuildRequires:	readline readline-devel ncurses ncurses-devel
Requires:		readline ncurses
%endif
Provides:	routingdaemon
Provides:	bird gated mrt zebra
Requires:	%{libname} = %{version}

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
%autosetup -p1

%build
export CFLAGS="%{optflags} -fPIC"

%serverbuild
slibtoolize --force
autoreconf -fi
%configure \
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
%if %{with_ospfclient}
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
%if %{with_pim}
    --enable-pimd \
%endif
%if %{with_pam}
    --with-libpam \
%endif
    --enable-user=%{quagga_user} \
    --enable-group=%{quagga_user} \
    --enable-vty-group=%{vty_group} \
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

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/pam.d
install -d %{buildroot}/var/log/quagga
install -d %{buildroot}/var/run/quagga
install -d %{buildroot}%{_infodir}


%makeinstall_std

# Remove this file, as it is uninstalled and causes errors when building on RH9
rm -rf %{buildroot}/usr/share/info/dir

mkdir -p %{buildroot}%{_unitdir}
install -m755 %{zeb_rh_src}/zebra.service %{buildroot}%{_unitdir}/
install -m755 %{zeb_rh_src}/bgpd.service %{buildroot}%{_unitdir}/
%if %{with_ipv6}
install -m755 %{zeb_rh_src}/ospf6d.service %{buildroot}%{_unitdir}/
install -m755 %{zeb_rh_src}/ripngd.service %{buildroot}%{_unitdir}/
%endif
install -m755 %{zeb_rh_src}/ospfd.service %{buildroot}%{_unitdir}/
install -m755 %{zeb_rh_src}/ripd.service %{buildroot}%{_unitdir}/
%if %{with_isisd}
install -m755 %{zeb_rh_src}/isisd.service %{buildroot}%{_unitdir}/
%endif
install -m755 %{zeb_rh_src}/nhrpd.service %{buildroot}%{_unitdir}/
install -m755 %{zeb_rh_src}/pimd.service %{buildroot}%{_unitdir}/
install -m644 %{zeb_rh_src}/quagga.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/quagga
install -m644 %{zeb_rh_src}/quagga.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/quagga

install -m644 %{zeb_rh_src}/quagga.pam %{buildroot}%{_sysconfdir}/pam.d/quagga

# nuke rpath
chrpath -d %{buildroot}%{_bindir}/*
chrpath -d %{buildroot}%{_sbindir}/*

rm -f %{buildroot}%{_libdir}/*.*a

mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/%{name}.conf <<EOF
g %{vty_group}
u %{quagga_user} - "Quagga Routing" %{_localstatedir}/lib %{_sbindir}/nologin
EOF

%post
# Create dummy files if they don't exist so basic functions can be used.
if [ ! -e %{_sysconfdir}/quagga/zebra.conf ]; then
	echo "hostname `hostname`" > %{_sysconfdir}/quagga/zebra.conf
	chown %{quagga_user}:%{quagga_user} %{_sysconfdir}/quagga/zebra.conf
	chmod 640 %{_sysconfdir}/quagga/zebra.conf
fi
if [ ! -e %{_sysconfdir}/quagga/vtysh.conf ]; then
	touch %{_sysconfdir}/quagga/vtysh.conf
	chmod 640 %{_sysconfdir}/quagga/vtysh.conf
fi

%files
%doc */*.sample* AUTHORS COPYING doc/quagga.html doc/mpls
%doc ChangeLog INSTALL NEWS README REPORTING-BUGS SERVICES TODO
%{_sysusersdir}/*.conf
#
%dir %attr(0751,%{quagga_user},%{quagga_user}) %{_sysconfdir}/quagga
%dir %attr(0750,%{quagga_user},%{quagga_user}) /var/log/quagga
%dir %attr(0751,%{quagga_user},%{quagga_user}) /var/run/quagga
#
%attr(0640,%{quagga_user},%{vty_group}) %config(noreplace) %{_sysconfdir}/quagga/vtysh.conf*
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
%if %{with_pim}
%config(noreplace) %{_sysconfdir}/quagga/pimd.conf*
%endif
#
%attr(0755,root,root) %{_unitdir}/bgpd.service
%attr(0755,root,root) %{_unitdir}/ospf6d.service
%attr(0755,root,root) %{_unitdir}/ospfd.service
%attr(0755,root,root) %{_unitdir}/ripd.service
%attr(0755,root,root) %{_unitdir}/ripngd.service
%attr(0755,root,root) %{_unitdir}/nhrpd.service
%attr(0755,root,root) %{_unitdir}/zebra.service
%if %{with_pim}
%attr(0755,root,root) %{_unitdir}/pimd.service
%endif
#
%{_sbindir}/bgpd
%{_sbindir}/ospf6d
%{_sbindir}/ospfclient
%{_sbindir}/ospfd
%{_sbindir}/ripd
%{_sbindir}/ripngd
%{_sbindir}/watchquagga
%{_sbindir}/zebra
%{_bindir}/bgp_btoa
%{_bindir}/nhrpd
%if %{with_pim}
%{_sbindir}/pimd
%{_bindir}/test_igmpv3_join
%endif
#
%if %{with_vtysh}
%{_bindir}/vtysh
%attr(0644,root,root) %{_mandir}/man1/vtysh.1*
%endif
#
%if %{with_isisd}
%attr(0755,root,root) %{_unitdir}/isisd.service
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
%{_mandir}/man8/nhrpd.8*
%{_mandir}/man8/ospfclient.8*
%{_mandir}/man8/watchquagga.8*
%if %{with_pim}
%attr(0644,root,root) %{_mandir}/man8/pimd.8*
%endif
%{_infodir}/*info*

%files contrib
%doc tools

%files -n %{libname}
%{_libdir}/*.so.*

%files -n %{develname}
%{_libdir}/*.so
%dir %{_includedir}/quagga
%{_includedir}/quagga/*.h
%{_includedir}/quagga/ospfapi
%{_includedir}/quagga/ospfd
