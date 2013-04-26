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
Version:        0.99.20.1
Release:        %mkrel 1
License:	GPL
Group:		System/Servers
URL:		http://www.quagga.net
Source0:	http://www.quagga.net/download/%{name}-%{version}.tar.gz
Source2:	http://download-mirror.savannah.gnu.org/releases/qpimd/qpimd-0.162.tar.gz
Source3:	pimd.init
Patch0:         quagga-0.99.11-netlink.patch
Patch1:		quagga-0.96.5-nostart.patch
Patch3:		quagga-0.99.10-libcap.diff
Patch100:	pimd-0.162-quagga-0.99.20.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	texinfo
BuildRequires:  texi2html
BuildRequires:  texlive
#BuildRequires:	tetex-texi2html
#BuildRequires:	tetex
BuildRequires:	pam-devel
BuildRequires:	libpcap-devel
BuildRequires:	chrpath >= 0.12
BuildRequires:	autoconf automake libtool
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
Provides:	routingdaemon
Obsoletes:	bird gated mrt zebra
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

%setup  -q
%patch0 -p1 -b .netlink
%patch1 -p1 -b .nostart
%patch3 -p0 -b .libcap

%if %{with_pim}
tar xzf %{SOURCE2}
#patch -p1 --fuzz=0 < qpimd-0.162/pimd-0.162-quagga-0.99.17.patch
%patch100 -p1
%endif

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
%if %{with_pim}
    --enable-pimd \
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

%if %{with_pim}
install -m755 %{SOURCE3} %{buildroot}%{_initrddir}/pimd
%endif

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

rm -f %{buildroot}%{_libdir}/*.*a

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

%files
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
%if %{with_pim}
%config(noreplace) %{_sysconfdir}/quagga/pimd.conf*
%endif
#
%attr(0755,root,root) %{_initrddir}/bgpd
%attr(0755,root,root) %{_initrddir}/ospf6d
%attr(0755,root,root) %{_initrddir}/ospfd
%attr(0755,root,root) %{_initrddir}/ripd
%attr(0755,root,root) %{_initrddir}/ripngd
%attr(0755,root,root) %{_initrddir}/watchquagga
%attr(0755,root,root) %{_initrddir}/zebra
%if %{with_pim}
%attr(0755,root,root) %{_initrddir}/pimd
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
%dir %{_includedir}/quagga/ospfd/*
#
%if %{with_ospfapi}
%dir %{_includedir}/quagga/ospfapi/*
%endif


%changelog
* Fri Mar 23 2012 Oden Eriksson <oeriksson@mandriva.com> 0.99.20.1-1mdv2012.0
+ Revision: 786342
- drop one file
- 0.99.20.1 (fixes CVE-2012-0249, CVE-2012-0250, CVE-2012-0255)
- various fixes

* Fri Sep 30 2011 Oden Eriksson <oeriksson@mandriva.com> 0.99.20-1
+ Revision: 702097
- 0.99.20
- simplify the pimd-0.162-quagga-0.99.18.diff patch
- drop upstream applied patches
- the quagga-0.99.11-fix-str-fmt.patch was silently fixed with no CVE assignment, well..., ok!
- 0.99.19 fixed CVE-2011-3323, CVE-2011-3324, CVE-2011-3325, CVE-2011-3326, CVE-2011-3327

* Fri Apr 01 2011 Oden Eriksson <oeriksson@mandriva.com> 0.99.18-1
+ Revision: 649653
- readd one rediffed patch
- 0.99.18

* Thu Mar 24 2011 zamir <zamir@mandriva.org> 0.99.17-3
+ Revision: 648238
- try pseudo patch
- wait fix error: texlive-20110312-1-mdv2011.0.x86_64 (due to unsatisfied texlive-texmf[*])
- try texi2html
- try again
- try again
- test requarements
- add pim-ssm support

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 0.99.17-2mdv2011.0
+ Revision: 627819
- don't force the usage of automake1.7

* Fri Aug 20 2010 Michael Scherer <misc@mandriva.org> 0.99.17-1mdv2011.0
+ Revision: 571432
- update to new version 0.99.17

* Thu Mar 11 2010 Oden Eriksson <oeriksson@mandriva.com> 0.99.16-1mdv2010.1
+ Revision: 517985
- 0.99.16

* Sun Aug 30 2009 Oden Eriksson <oeriksson@mandriva.com> 0.99.15-1mdv2010.0
+ Revision: 422370
- 0.99.15

* Wed Jul 22 2009 Oden Eriksson <oeriksson@mandriva.com> 0.99.14-1mdv2010.0
+ Revision: 398483
- 0.99.14

* Thu Jun 25 2009 Frederik Himpe <fhimpe@mandriva.org> 0.99.13-1mdv2010.0
+ Revision: 389184
- update to new version 0.99.13

* Sun May 10 2009 Oden Eriksson <oeriksson@mandriva.com> 0.99.12-1mdv2010.0
+ Revision: 373982
- 0.99.12 (fixes CVE-2009-1572)

* Fri Apr 03 2009 Funda Wang <fwang@mandriva.org> 0.99.11-2mdv2009.1
+ Revision: 363812
- bump rel
- fix str fmt
- rediff netlink patch

* Sat Oct 11 2008 Oden Eriksson <oeriksson@mandriva.com> 0.99.11-1mdv2009.1
+ Revision: 291860
- 0.99.11

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 0.99.10-2mdv2009.0
+ Revision: 269101
- rebuild early 2009.0 package (before pixel changes)

* Wed Jun 11 2008 Oden Eriksson <oeriksson@mandriva.com> 0.99.10-1mdv2009.0
+ Revision: 218009
- 0.99.10
- use _disable_ld_no_undefined to fix linkage
- added P3 to fix other linkage
- use the %%serverbuild macro

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Sep 13 2007 Oden Eriksson <oeriksson@mandriva.com> 0.99.9-1mdv2008.1
+ Revision: 84923
- 0.99.9

* Mon Aug 27 2007 Thierry Vignaud <tv@mandriva.org> 0.99.7-2mdv2008.0
+ Revision: 72252
- fix info-install requires
- convert prereq
- kill file require on info-install

* Mon Jul 02 2007 Andreas Hasenack <andreas@mandriva.com> 0.99.7-1mdv2008.0
+ Revision: 47301
- updated to version 0.99.7 (fixes #30596)


* Wed Mar 07 2007 Oden Eriksson <oeriksson@mandriva.com> 0.99.6-1mdv2007.0
+ Revision: 134493
- Import quagga

* Wed Mar 07 2007 Oden Eriksson <oeriksson@mandriva.com> 0.99.6-1mdv2007.1
- 0.99.6
- synced patches with fc (0.98.6-3.fc7)
- enable -fstack-protector

* Tue Feb 21 2006 Oden Eriksson <oeriksson@mandriva.com> 0.99.3-1mdk
- 0.99.3
- use dynamic uid/gid
- rediff P0 and install the pam_stack.so version if needed

* Wed Aug 31 2005 Oden Eriksson <oeriksson@mandriva.com> 0.98.5-1mdk
- 0.98.5
- fix deps

* Wed Jun 29 2005 Oden Eriksson <oeriksson@mandriva.com> 0.98.4-1mdk
- 0.98.4

* Sat Apr 09 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.98.3-1mdk
- 0.98.3
- use the %%mkrel macro
- misc rpmlint fixes

* Fri Feb 04 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.98.0-2mdk
- rebuilt against new readline

* Tue Jan 18 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.98.0-1mdk
- 0.98.0

* Fri Dec 31 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 0.97.4-3mdk
- revert latest "lib64 fixes"
- fixed the install info error
- make it require the explicit libname version

* Wed Dec 29 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 0.97.4-2mdk
- make it compile on 10.0

* Tue Dec 28 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 0.97.4-1mdk
- 0.97.4
- rediffed P0
- added watchquagga
- use the %%configure2_5x macro and libifiction
- nuke rpath
- misc spec file fixes

* Wed Aug 18 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 0.96.5-1mdk
- quagga-0.96.5 (the zebra fork, fedora import)

* Wed Jun 16 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 05 2004 Jay Fenlason <fenlason@redhat.com> 0.96.5-0
- New upstream version
- Change includedir
- Change the pre scriptlet to fail if the useradd command fails.
- Remove obsolete patches from this .spec file and renumber the two
  remaining ones.

