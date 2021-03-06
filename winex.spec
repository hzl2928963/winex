#
# Conditional build:
%bcond_without	arts		# without arts support
%bcond_without	cups		# without CUPS printing support
%bcond_without	sane		# without TWAIN scanning support (through SANE)
%bcond_with	pdf_docs	# build pdf docs (missing BR)
%bcond_with	html_docs	# build html docs (jade fault ?)
%bcond_with	nptl		# build with posix threads
#
# maybe TODO: alsa,jack,nas BRs/checks (see dlls/winmm/wine*)
Summary:	Program that lets you launch Win applications
Summary(es.UTF-8):	Ejecuta programas Windows en Linux
Summary(pl.UTF-8):	Program pozwalający uruchamiać aplikacje Windows
Summary(pt_BR.UTF-8):	Executa programas Windows no Linux
Name:		winex
Version:	3.3.1
Release:	0.1
License:	Aladdin FPL and partially LGPL
Group:		Applications/Emulators
Source0:	%{name}-%{version}.tar.bz2
# Source0-md5:	0af59d188f3d937348eee492326bb7a9
#Source1:	%{name}.init
Source2:	%{name}.reg
Source3:	%{name}.systemreg
Source4:	%{name}.userreg
Patch0:		%{name}-fontcache.patch
Patch1:		%{name}-destdir.patch
Patch2:		%{name}-ncurses.patch
Patch3:		%{name}-flex.patch
Patch4:		%{name}-binutils.patch
Patch5:		%{name}-makedep.patch
Patch6:		%{name}-build.patch
URL:		http://www.winehq.com/
BuildRequires:	OpenGL-devel
BuildRequires:	XFree86-OpenGL-devel-base
BuildRequires:	XFree86-devel
%{?with_arts:BuildRequires:	arts-devel}
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	chpax
%{?with_cups:BuildRequires:	cups-devel}
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	docbook-utils
BuildRequires:	flex
BuildRequires:	freetype-devel >= 2.0.5
BuildRequires:	libjpeg-devel
BuildRequires:	ncurses-devel
%if %{with html_docs} || %{with pdf_docs}
BuildRequires:	openjade
%endif
%if %{with pdf_docs}
BuildRequires:	tetex-fonts-pazo
BuildRequires:	tetex-fonts-stmaryrd
BuildRequires:	tetex-fonts-type1-urw
BuildRequires:	tetex-metafont
%endif
%{?with_sane:BuildRequires:	sane-backends-devel}
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires:	OpenGL
# link to wine/ntdll.dll.so, without any SONAME
Provides:	libntdll.dll.so
ExclusiveArch:	%{ix86}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep		libGL.so.1 libGLU.so.1
%define		no_install_post_strip	1

%define		_winedir		%{_datadir}/%{name}

%description
Wine is a program which allows running Microsoft Windows programs
(including DOS, Windows 3.x and Win32 executables) on Unix. It
consists of a program loader which loads and executes a Microsoft
Windows binary, and a library that implements Windows API calls using
their Unix or X11 equivalents. The library may also be used for
porting Win32 code into native Unix executables.

%description -l es.UTF-8
Ejecuta programas Windows en Linux.

%description -l pl.UTF-8
Wine jest programem dzięki któremu można uruchamiać programy napisane
dla Microsoft Windows pod systemami uniksowymi. Składa się on z
loadera, który pozwala wczytywać i uruchamiać programy w formacie
Microsoft Windows oraz z biblioteki, która implementuje API Windows
przy użyciu odpowiedników uniksowych oraz z X11. Biblioteka może być
także wykorzystana do przenoszenia aplikacji Win32 do Uniksa.

%description -l pt_BR.UTF-8
O Wine é um programa que permite rodar programas MS-Windows no X11.
Ele consiste de um carregador de programa, que carrega e executa um
binário MS-Windows, e de uma biblioteca de emulação que traduz as
chamadas da API para as equivalentes Unix/X11.

%package devel
Summary:	Wine - header files
Summary(es.UTF-8):	Biblioteca de desarrollo de wine
Summary(pl.UTF-8):	Wine - pliki nagłowkowe
Summary(pt_BR.UTF-8):	Biblioteca de desenvolvimento do wine
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Wine - header files.

%description devel -l es.UTF-8
Biblioteca de desarrollo de wine.

%description devel -l pl.UTF-8
Wine - pliki nagłówkowe.

%description devel -l pt_BR.UTF-8
Arquivos de inclusão e bibliotecas para desenvolver aplicações com o
WINE.

%package programs
Summary:	Wine - programs
Summary(pl.UTF-8):	Wine - programy
Group:		Applications
Requires:	%{name} = %{version}-%{release}

%description programs
Wine - programs.

%description programs -l pl.UTF-8
Wine - programy.

%package doc-pdf
Summary:	Wine documentation in PDF
Summary(pl.UTF-8):	Dokumentacja Wine w formacie PDF
Group:		Documentation

%description doc-pdf
Wine documentation in PDF format.

%description doc-pdf -l pl.UTF-8
Dokumentacja Wine w formacie PDF.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p0
%patch5 -p1
%patch6 -p1

# turn off compilation of some tools
#sed -e "s|winetest \\\|\\\|;s|avitools||" programs/Makefile.in > .tmp
sed -e "s|wcmd\|winetest\|winhelp\|avitools||" programs/Makefile.in > .tmp
mv -f .tmp programs/Makefile.in

%build
%{__aclocal}
%{__autoconf}
CFLAGS="%{rpmcflags} -DALSA_PCM_OLD_HW_PARAMS_API"; export CFLAGS
CPPFLAGS=$CFLAGS; export CPPFLAGS
LDFLAGS="%{rpmldflags} %{?with_nptl:-lpthread}"; export LDFLAGS
%configure \
	%{!?debug:--disable-debug} \
	%{!?debug:--disable-trace} \
	--enable-curses \
	--enable-opengl \
	%{?with_nptl:--enable-pthreads} \
	--with-x
%{__make} depend
%{__make}
%{__make} -C programs
%{__make} -C programs/regapi

cd documentation
%if %{with html_docs}
db2html wine-user.sgml
db2html wine-devel.sgml
db2html wine-faq.sgml
db2html winelib-user.sgml
%endif

%if %{with pdf_docs}
db2pdf 	wine-user.sgml
db2pdf	wine-devel.sgml
db2pdf	wine-faq.sgml
db2pdf	winelib-user.sgml
%endif
cd -

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_mandir}/man1,%{_aclocaldir}}

%{__make} install \
	prefix=$RPM_BUILD_ROOT%{_prefix} \
	exec-prefix=$RPM_BUILD_ROOT%{_exec_prefix} \
	bindir=$RPM_BUILD_ROOT%{_bindir} \
	sbindir=$RPM_BUILD_ROOT%{_sbindir} \
	sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
	datadir=$RPM_BUILD_ROOT%{_datadir} \
	includedir=$RPM_BUILD_ROOT%{_includedir}/winex \
	libdir=$RPM_BUILD_ROOT%{_libdir} \
	libexecdir=$RPM_BUILD_ROOT%{_libexecdir} \
	localstatedir=$RPM_BUILD_ROOT%{_localstatedir} \
	sharedstatedir=$RPM_BUILD_ROOT%{_sharedstatedir} \
	mandir=$RPM_BUILD_ROOT%{_mandir} \
	infodir=$RPM_BUILD_ROOT%{_infodir} \
#	dlldir=$RPM_BUILD_ROOT%{_libdir}/winex

%{__make} -C programs install \
	DESTDIR=$RPM_BUILD_ROOT

#install programs/winhelp/hlp2sgml	$RPM_BUILD_ROOT%{_bindir}
#install tools/fnt2bdf			$RPM_BUILD_ROOT%{_bindir}

install aclocal.m4 $RPM_BUILD_ROOT%{_aclocaldir}/wine.m4
#mv -f $RPM_BUILD_ROOT{/usr/X11R6/share/aclocal,%{_aclocaldir}}/wine.m4

install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d \
	$RPM_BUILD_ROOT%{_winedir}/windows/{system,Desktop,Favorites,Fonts} \
	"$RPM_BUILD_ROOT%{_winedir}/windows/Start Menu/Programs/Startup" \
	$RPM_BUILD_ROOT%{_winedir}/windows/{SendTo,ShellNew,system32,NetHood} \
	$RPM_BUILD_ROOT%{_winedir}/windows/{Profiles/Administrator,Recent} \
	$RPM_BUILD_ROOT%{_winedir}/{"Program Files/Common Files","My Documents"}

#install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/winex
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}

touch $RPM_BUILD_ROOT%{_winedir}/{autoexec.bat,config.sys,windows/win.ini}
touch $RPM_BUILD_ROOT%{_winedir}/windows/system/{shell.dll,shell32.dll}
touch $RPM_BUILD_ROOT%{_winedir}/windows/system/{winsock.dll,wsock32.dll}

cat >$RPM_BUILD_ROOT%{_winedir}/windows/system.ini <<EOF
[mci]
cdaudio=mcicda.drv
sequencer=mciseq.drv
waveaudio=mciwave.drv
avivideo=mciavi.drv
videodisc=mcipionr.drv
vcr=mciviscd.drv
MPEGVideo=mciqtz.drv
EOF

%if %{?debug:0}%{!?debug:1}
echo "Strip executable binaries and shared object files."
filelist=`find $RPM_BUILD_ROOT -type f ! -regex ".*ld-[0-9.]*so.*"`
elfexelist=`echo $filelist | xargs -r file | \
	awk '/ELF.*executable/ {print $1}' | cut -d: -f1`
elfsharedlist=`echo $filelist | xargs -r file | \
	awk '/LF.*shared object/ {print $1}' | cut -d: -f1`; \
if [ -n "$elfexelist" ]; then \
	strip -R .note -R .comment $elfexelist
fi
if [ -n "$elfsharedlist" ]; then
	strip --strip-unneeded -R .note -R .comment $elfsharedlist
fi
%endif

# /sbin/chstk -e $RPM_BUILD_ROOT%{_bindir}/wine

programs="notepad progman regsvr32 uninstaller wineconsole winemine clock cmdlgtst control osversioncheck regapi regtest view winedbg winver"

rm -f files.programs; touch files.programs
for p in $programs; do
	echo "%attr(755,root,root) %{_bindir}/$p" >> files.programs
	echo "%attr(755,root,root) %{_bindir}/$p.so" >> files.programs
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
#/sbin/chkconfig --add winex
#if [ ! -f /var/lock/subsys/wine ]; then
#	echo "Run \"/etc/rc.d/init.d/winex start\" to start winex service." >&2
#fi

#%preun
#if [ "$1" = "0" ]; then
#	if [ -f /var/lock/subsys/wine ]; then
#		/etc/rc.d/init.d/winex stop >&2
#	fi
#	/sbin/chkconfig --del winex
#fi

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README DEVELOPERS-HINTS ChangeLog BUGS AUTHORS ANNOUNCE LICENSE LICENSE.ReWind
#%doc documentation/wine-user
%attr(755,root,root) %{_bindir}/wine
%attr(755,root,root) %{_bindir}/wine_relocated
%attr(755,root,root) %{_bindir}/widl
%attr(755,root,root) %{_bindir}/winebuild
%attr(755,root,root) %{_bindir}/winemaker
%attr(755,root,root) %{_bindir}/wineserver
%attr(755,root,root) %{_bindir}/wineclipsrv
%attr(755,root,root) %{_bindir}/winelauncher
%attr(755,root,root) %{_bindir}/wineshelllink
%attr(755,root,root) %{_bindir}/winedump
%attr(755,root,root) %{_bindir}/wrc
%attr(755,root,root) %{_bindir}/wmc
%attr(755,root,root) %{_bindir}/fnt2bdf
%attr(755,root,root) %{_bindir}/function_grep.pl
%attr(755,root,root) %{_libdir}/*.so*
#%%{_libdir}/winex
%{_mandir}/man[15]/*
%config(noreplace) %{_sysconfdir}/winex.reg
%config(missingok) %{_sysconfdir}/winex.systemreg
%config(missingok) %{_sysconfdir}/winex.userreg
#%attr(754,root,root) %{_sysconfdir}/rc.d/init.d/winex
%{_winedir}

%files devel
%defattr(644,root,root,755)
#%doc documentation/{wine-devel,winelib-user,HOWTO-winelib}
%{_includedir}/winex
%{_libdir}/*.a
%{_aclocaldir}/*.m4

%files programs -f files.programs
%defattr(644,root,root,755)
