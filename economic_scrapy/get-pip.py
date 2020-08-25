#!/usr/bin/env python
#
# Hi There!
# You may be wondering what this giant blob of binary data here is, you might
# even be worried that we're up to something nefarious (good for you for being
# paranoid!). This is a base85 encoding of a zip file, this zip file contains
# an entire copy of pip (version 20.2.1).
#
# Pip is a thing that installs packages, pip itself is a package that someone
# might want to install, especially if they're looking to run this get-pip.py
# script. Pip has a lot of code to deal with the security of installing
# packages, various edge cases on various platforms, and other such sort of
# "tribal knowledge" that has been encoded in its code base. Because of this
# we basically include an entire copy of pip inside this blob. We do this
# because the alternatives are attempt to implement a "minipip" that probably
# doesn't do things correctly and has weird edge cases, or compress pip itself
# down into a single file.
#
# If you're wondering how this is created, it is using an invoke task located
# in tasks/generate.py called "installer". It can be invoked by using
# ``invoke generate.installer``.

import os.path
import pkgutil
import shutil
import sys
import struct
import tempfile

# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    iterbytes = iter
else:
    def iterbytes(buf):
        return (ord(byte) for byte in buf)

try:
    from base64 import b85decode
except ImportError:
    _b85alphabet = (b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    b"abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")

    def b85decode(b):
        _b85dec = [None] * 256
        for i, c in enumerate(iterbytes(_b85alphabet)):
            _b85dec[c] = i

        padding = (-len(b)) % 5
        b = b + b'~' * padding
        out = []
        packI = struct.Struct('!I').pack
        for i in range(0, len(b), 5):
            chunk = b[i:i + 5]
            acc = 0
            try:
                for c in iterbytes(chunk):
                    acc = acc * 85 + _b85dec[c]
            except TypeError:
                for j, c in enumerate(iterbytes(chunk)):
                    if _b85dec[c] is None:
                        raise ValueError(
                            'bad base85 character at position %d' % (i + j)
                        )
                raise
            try:
                out.append(packI(acc))
            except struct.error:
                raise ValueError('base85 overflow in hunk starting at byte %d'
                                 % i)

        result = b''.join(out)
        if padding:
            result = result[:-padding]
        return result


def bootstrap(tmpdir=None):
    # Import pip so we can use it to install pip and maybe setuptools too
    from pip._internal.cli.main import main as pip_entry_point
    from pip._internal.commands.install import InstallCommand
    from pip._internal.req.constructors import install_req_from_line

    # Wrapper to provide default certificate with the lowest priority
    # Due to pip._internal.commands.commands_dict structure, a monkeypatch
    # seems the simplest workaround.
    install_parse_args = InstallCommand.parse_args
    def cert_parse_args(self, args):
        # If cert isn't specified in config or environment, we provide our
        # own certificate through defaults.
        # This allows user to specify custom cert anywhere one likes:
        # config, environment variable or argv.
        if not self.parser.get_default_values().cert:
            self.parser.defaults["cert"] = cert_path  # calculated below
        return install_parse_args(self, args)
    InstallCommand.parse_args = cert_parse_args

    implicit_pip = True
    implicit_setuptools = True
    implicit_wheel = True

    # Check if the user has requested us not to install setuptools
    if "--no-setuptools" in sys.argv or os.environ.get("PIP_NO_SETUPTOOLS"):
        args = [x for x in sys.argv[1:] if x != "--no-setuptools"]
        implicit_setuptools = False
    else:
        args = sys.argv[1:]

    # Check if the user has requested us not to install wheel
    if "--no-wheel" in args or os.environ.get("PIP_NO_WHEEL"):
        args = [x for x in args if x != "--no-wheel"]
        implicit_wheel = False

    # We only want to implicitly install setuptools and wheel if they don't
    # already exist on the target platform.
    if implicit_setuptools:
        try:
            import setuptools  # noqa
            implicit_setuptools = False
        except ImportError:
            pass
    if implicit_wheel:
        try:
            import wheel  # noqa
            implicit_wheel = False
        except ImportError:
            pass

    # We want to support people passing things like 'pip<8' to get-pip.py which
    # will let them install a specific version. However because of the dreaded
    # DoubleRequirement error if any of the args look like they might be a
    # specific for one of our packages, then we'll turn off the implicit
    # install of them.
    for arg in args:
        try:
            req = install_req_from_line(arg)
        except Exception:
            continue

        if implicit_pip and req.name == "pip":
            implicit_pip = False
        elif implicit_setuptools and req.name == "setuptools":
            implicit_setuptools = False
        elif implicit_wheel and req.name == "wheel":
            implicit_wheel = False

    # Add any implicit installations to the end of our args
    if implicit_pip:
        args += ["pip"]
    if implicit_setuptools:
        args += ["setuptools"]
    if implicit_wheel:
        args += ["wheel"]

    # Add our default arguments
    args = ["install", "--upgrade", "--force-reinstall"] + args

    delete_tmpdir = False
    try:
        # Create a temporary directory to act as a working directory if we were
        # not given one.
        if tmpdir is None:
            tmpdir = tempfile.mkdtemp()
            delete_tmpdir = True

        # We need to extract the SSL certificates from requests so that they
        # can be passed to --cert
        cert_path = os.path.join(tmpdir, "cacert.pem")
        with open(cert_path, "wb") as cert:
            cert.write(pkgutil.get_data("pip._vendor.certifi", "cacert.pem"))

        # Execute the included pip and use it to install the latest pip and
        # setuptools from PyPI
        sys.exit(pip_entry_point(args))
    finally:
        # Remove our temporary directory
        if delete_tmpdir and tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    tmpdir = None
    try:
        # Create a temporary working directory
        tmpdir = tempfile.mkdtemp()

        # Unpack the zipfile into the temporary directory
        pip_zip = os.path.join(tmpdir, "pip.zip")
        with open(pip_zip, "wb") as fp:
            fp.write(b85decode(DATA.replace(b"\n", b"")))

        # Add the zipfile to sys.path so that we can import it
        sys.path.insert(0, pip_zip)

        # Run the bootstrap
        bootstrap(tmpdir=tmpdir)
    finally:
        # Clean up our temporary working directory
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


DATA = b"""
P)h>@6aWAK2mtj%1X1Lt_Z1@n0074U000jF003}la4%n9X>MtBUtcb8d2NtyOT#b_hu`N@9QB18%v6V
<4kpO(&rrJ|`eKX`vh}(J+9c$zj(&U7jVi)I-sG3#xx1$bt^#koRK_v}t4mq4DM@nUjopH&ybBEPi}^
xLULGf}>f<ZRrrEO)rZ^Fg1jJLc)c=GxLp*?)XX9cMA%s%j7%0A!f-xk+OF5KRN&LvMfJz(N(_u^F%v
tOosb?(`N6_mi%NDvM4y#okF76?&a41ZY<a1{T;?)+q#o%E+1!v0!D%6&tZ~<yUSU0VJa{{-wuyK}Li
9nlRJd+d$;8QHsd2WtvAxGBH(Etb$cFdkeX}UGMtJiYls?;}Lr;(W&q8cf^xxTxV-DH1)PH9KWq46%J
)R|NJpuNX%93>#v!TyE^NqzAHP)h>@6aWAK2mtj%1W{-R4?Nfb0055z000jF003}la4%n9ZDDC{Utcb
8d0kS$j+`(Iz4H~8<^WVIJLgqrr5<}-^;T6;8q5#@Ng9Wt^y_P9ptD;}#IfIdelLCWGbq(BX^E&5*g5
!^K>s8^EeX~AToilV)A2_e6~zhOaP~KZvIOlqFiVW+60AOs)?J~q5l!-OgI;*jfY94W3Aib4Jnnk|YJ
*Ng1Ga|{kpv)l&^K>8SV(XV+<$mHY8?a{!1#G)Y63H$85<@-{DTbUDCucxV6x07;%M+|!-MO9j<0Wi#
11q;*wWw~Jk1&J^A7l0*oU_7=O4mXm1V;gv{y`K?W($dDS*GDs|`L>=UQy}+QW*VBSKu9lNGW7TF8+_
>8{Ie<fCkRVDRj>!4j}^zf$g5NMG?#$r7JFwd*iFi`ae1M^!{C6|@<7hU2_kIGVf4lf-PN95Q{xc~)x
H)+yD7ZSTFu#C|(HBN!o}6m1}htb9MfmJk{*1|JR5!La3y^@g-eNlcIpg<aOlzzp`V!6w3~--o_rhje
;x4v-gHjdsU7WtQBZZ!eNf4r13`{eM0jsOyixv5y#2b#5{cCz#V>@K#xukcX$%OtzJ!59<8S&nG(}iY
;;Zg+|Wh1kV4`#XSvS-lI5dD<2OBf7?{$GQX$dFHlPZ1QY-O00;o}Lj+M_Od3ur0RRB+0RR9Q0001RX
>c!JX>N37a&BR4FJE72ZfSI1UoLQYZIMq)!$1(l@B1l+_R>O4E`nOnOYt9S712W}C2W&PGm`ACGZQ7>
-fcn^q01hYVcwfJzojO4RtOZ5jGQ7nTPLkjEeW{~%rz6tTSjH;q;G{WIR9x)$-X(N(=L$P0S(SitCv-
_xVv6FWUueb<^A&37%GpH=LX{GUH>~g2PGfvXYfd(#+U+2Xe_yj<(*tEy~F7s9`BVnhsi;*-YeFkyxC
0Q<O*WazHu}fy;UR-Z(tPUFD#(+48ATP_fC9`AURV|0j;dYc^ybxuZArGV~LC|k0E<I(!}(Sn`mK+f`
;i(pxQ`e27(BcYLI!F?ntY4o8-PpLl<ls5vC;4qNHc17w5?#;2(}-kkKi3!N;l`IAz~#LqHy)#4l^v{
T6#xQ}Y8*O9KQH000080QExzQDQrDSaJyf0GJ;D02%-Q0B~t=FJEbHbY*gGVQepAb!lv5UuAA~E^v9}
S>1EnxDkKXUx7LgB&Q^&>7%CV%*Amoo~E`ZcCM4rXgCxJ$v9I43s91E8UOFy#RmzHl#}bdwR({V?k@J
@w~NK<;^N}no>e8est-)?dPnP)>?JM9h6}<Zukx1hnv{FN>MfBalPy^z2RzO$E-q#>wrjX(NyWEYTr-
bc+F$b2{cP!TdlY#y+X%iR1+OYvpm<3P!L2B%pyhj3w3-I@+qbNeDTpa}y<uBRyQOW`oZ3fTXBAs(@@
b;HeUvjz(6A=W4zw=0NSmi^CaC0lQP56<&-CAWCMfzLCcjW2LA^^5S%FG1`4<;YVB|e*dwG^K%Qmc{S
w?b+%UQ(><vV9%R<~5td6gCwOJ&3A8aA-}yrFew7N>ZO8}{o)a8S78EApz!`sMSiE!{O)$%JKmfamvM
YteFXiV41kw;32%z9!|=AQFs>e}29Dnq7Xpy8K7>`OD4C_07)!h|R?Ed`94-q=JOr-wz@$=sGW+9$?j
@advswHx-QuxIHG<piREU$J++on^!UU1SpA#FTvLxY@*L;1N-D#3W0*h&JTBb^@CcR%@D}&a$ymj0){
@RwJ^)-d<P+pX0usQ<q(7HPS6c|p3l_ACEWlFSk2lj3ni^KF+uP}+IalDQP$5%C|ePc<nQE$*R*?!EG
crp?)c@ukhI-5@a98a$pO!r)he=!9`IpDfuEpm0|J5JGDQ=}VxgBPh$2D5C40^qWl9ixjE7vv#kXLcO
B&3TQZdj&Rd7~bI*w==$U?BDmBGrf`G&V(Gs*|Yb}1b=>DqGCoV1VBVS}_5xj3mkB$1rlo$gLhl%R45
gl%;qa^GMKX_<C>&0bL8w7%#nM2K2Lg3*F)Sg}xEjEOdSp~BRQ0LmW_@gVl+B!H_sJr-8p-1Dpo9IRs
CBy6=b487wpI6uY{+bvcdGF4f3s(Q%Rzk<&U7NK%q3Yxc&h<RO-U0y>5;BQm&;Q*k{i2&hYwQQl%=;9
AZZ=@A;2K!T}A49$?N(;Xp`S8V>wD1a4`tHm1r}x>_%`Y+8R(uVroic4ksRGkua^~lX!8t|$Ip<C2?-
*j5#5TV}$QulB`YUI3Xmw6?Iv`~fMIJkzo+{B;O~Rn&VwYC|WDY-2QRSzgr;bMYnPgV+UG>hxBDaLHu
^N!OaCns*b<(z@R)T^maL|Vp5Qe^I(nDVDsSLrY3H)^mrg;NrRvBtGTZEzs4y$7d4S>U8mmL?pA(wmE
@*Vq)63JQ$&~tH=04yb7o}>*_Njz`?wD1TC${~;*WrHRHc=JLXmw;iYHxN55*PI2i_ojN8;Y;-8H_r?
ke~e@Sl`llHNV!x=!!Uac`1yYQiQ?bKguou~^zMEc00R{>sr4Fs1EdSQ(pB@eW1-K04;lI*2e1Iz-4i
SisXC$~gJ@xc<0q0&Zd563{L=>V1Qw4$ggw=!@i*Nx=}`cEXuHa^q$L)*kxPRh7_D_}YODent2T8+^@
e-^ctUSc3f>rmBpM-5cU75Ghf_M@<bpx-kV9v7l9@Tu;iocwIbV(FpK5-r^~sHtv<;&XjY?n?1!()`!
u3z$Wj><D557(FvczwUkB+#r*TVTd-q7sfYBjmdC_DVa@SF{uKPm*q&|%Spm&P)u{JfmpS-o_(AF)od
>85GIJe4Kdiq1(R31bti(U_GZ1ttJ^PoYIBV**jch6vgxeL^xifx0)kJYwtI6-ZSd&E>%DlkCSsm95B
U5e2OUg}g!Ahhh9-1dgLP%+M&^;E@UEl7sSv`w$bW>cT%_?0KsD5sDXp-_?+qnv@?XFds$-0UqjeM1*
ON@OEH&1r+mI7jXB}!$<4^?!G>JyuG=({c?Zx`TqLhs$WwSZb9!mQd2>^^Vh8-yecz~$Xc+}`}ULwXh
ZCW*pz#9KwAp9rB<x9Ra?@=ZCCU$Ws}Y?=Bu8}an`;mp=gG_OSOV?(r=<q2L+XQKsxl@oCI%!NuqO7J
Ea}jFFt6VRTJw$qNk<LMTY2!dl=c9=n}7>%Xd&BuAU337FR2e@qpLWF`v)kZ?&G<$GtUc`YCj$X*vct
f)Z|Z8nYN@)$FN6_JET@BzMpQ`XDjrF+5U<9#;w{<PC4aZo6@cjPE!;|I+ZTuwL4Y`(PE1w0O!yKeUn
N-VIA~$|ZJupju<)95q~6-qUuef58jr2H@>VO&k<q9}>9le1?0tsL5aPJe0of2`S912urZ5)*Pt`-;m
H;q$t$%V-Dr1jFhsZ#ogsV+>S|kRur<iigmv&*RYXrl^eceTApvu5s&?T=oJo1?Wov+1bw#{3c^n-PS
a-!Y<-j|4rM}T{03<Y_mdE0MbUYr4NS(PMzM?tsY<WmNDmv!Gg2LADXBQJ3E?agTe<wpD$S(}JGd&1T
lvY4BjxSNy*3IBD`(r-TGiv-fX7GtnL?$fTu!<12VMQXy(ov+OO(FktBYF(#>28wv15RR9)Qqmz)s_r
KU}5EMRhT_voD7V^s2d?iN0Q{f!RP}H%0Si1m@1;WtkUF9h`nI2;ZpD#6E~V!~Lbz^GVw_LaJZ|3*Dh
G-fK)Oho@JPuq|F@lde!;gODUOPxfG;ez3DTYn5v3hjM`92-P#uBe}%x?QHn!ya1e{XQ9~RTx~Wut3S
|BaH+1KZ~9w5Abo%J?#s`<ztBN;JP;%Yr>Vg*p_{u5pxz2z*%=A;HMuycF-cvW?Bn17(!5g7=JFP@N#
i{Ag~o$TqOp3W)dBsIfc$wtp9%_B?}COwraT_Jmft}fm<z3%MTS;KF!ft7ud#3iFHz+7PHG^X?L~!_7
z_F}HwOLcgo}+0%OGK(W={$gYBes;KrQl2QK8cv^0)KVxC#z-NECabxDw!k4IP2bcH=YMhXVpr@eE*5
vHA)1vH^v!4A)*aJVCld(FL)Rv2y&3av!;D9l5R8!#$$RaQQo;4QYa;ARNC|-jQiULYnephJ_jOQP7G
)KQ|@1cLC4^Q<C(M++hEE5`Z$XSu#6AHhg2Ob4%UCoW}kU6`D$}CNO5r*J|+hQ;3_ymULmh`#(%>_-!
*9O%E6PA@xsCmlNKo`AecY3zd~>D2<^Va$3GWG?Q*X(LZ*H97*_}zESwr7J&YG-~89!`oC#$M9w6||H
iI&(D|csw7e363+T%K15ir?1QY-O00;o}Lj+MuGzp$Q3;+PxF8}}*0001RX>c!JX>N37a&BR4FJob2X
k{*NdF>kgkK4BOcmEZff+6yt=(<CeVa8k_O)pKbBrTFFg5q!xXo<F&$f8P0xwu9D_r3QhiKHx_FI~H$
Tm8eGP4Ydy?=LBeq9;7x3igs$d?R+EYGzRs&1P~}E8VayH``LK`k(KNs`~Gx+H7RC>3=FSo2|9lv0Bz
?_CZvI(rL}}_Z&~94c{2n9hFrhbgc#a%__bVNwD%kXd~g8TadMlEC*~kuT&*-UdkT?q4Vh=#1$`7@i7
;519%6x=hX**Dc){{D4)tw5a<NtP8FgwX(_AsJ?IPge#_AtMA@Gu{8NXCiL?>BIxD2^k6*&?FQpcFqx
3#uxDC76ds!9c7A*T3<kI7K`Q10)Wlx@6Jo#7l`rB8pp1=C)IAp7xBx~MmvqojG1_rR6z_XY!_z<%2%
CAYbyiC{|(Ig-s1AiY^z`>U?Z)Ohcv~^ta&G`ISz-y&<yvcG^HChdleoCuP?BZ;O_9--5_J*2nMDv2y
;*9Jh%jUD$tPpFKp_zjg@+L0kmdAU@pjfaN>Ay0KP8j^Tp0fv^;}<#uj`CVGt*#h{HNGkZGh2Rs{*b9
PEFnG=ir%N_QV3yy9Q2{IXm_=V3qT5#XYa+{EH8Bno?t}HH3#LJWgI0@!lFeqPnf7ot3}35E+w6u6Fz
OP@4Pg%x5p+GRSuGhBRU_==jm2_EaXO*CPtp~k{iRw@nf}m2gcTM4Rk&RZdSk{&%w3m+yho?^+6WGfU
jY!C_4L;umY-J1#h_37CH&U0m6l!1v0a<U})tFb_wuWsRl*Vz<1h8#{i*%7hp-u(urV!o;w;F1$XacG
a$mxN`ml_$dy1-)q)qD?H;|Dm!-N9MP>;w3wE=W`L?6S;O%P&6~<uzjjOgSK>td6=<pNYCj$2O8LtX<
->6pS0)A*g;HoP3{e28VQ7g>6SAvxwnI;&&Y_cpiqFg6VlF3L$$(Zy`qk%1x83*Dcf4v$k`<1H10A|`
6e1)t8?Xq0Y(}9}#a0;X^!1*fGIN}%>g)%9|lT;cor+C<MfQT`5Aj=Ruqy&$SoPIeHKzMj03^+YnaW<
M!8t_j37+F=J^H~i>KaJU)x+HBYaQ8UGH)qS`=n7A{5Rx*>HpO1B!Nz2z*zkPcDI7g&N|l&`NM#smNr
A%|u%E94MssZ~7QcYS@rLbM(||J!x_PH$1;%$Ho2`?+lgtYuq_cB~Q7ndN%>K#FKbw=^=V}LN<Vu#Z*
;_2CEFk6*gh_phW*!S~1-s!@gHF2<m4I+3z(p9O9b9S+`~t#T?QTxk4TK$4-EVqG58XTDN{a^wh>rE`
>leUe&hfVdrsZafh0F)w8@3_SLQ;inQ_<nI<{PSd96t2c;kq2%m9JEbB2>n6aUjbo3{2(<)r7e;Ln*-
FtjFur0tuB)QLe%K!=xd%K~twohi!jn5yX_?(v;UVWYIWUMx@60Dny<*Y}fO7Ks3sE$)bB5;DB=O>*#
_q2x$Q|k1(WQn_^HO_sf!5kxS#t8?IyqVsXi}htG(-)o3P=OCYQ?7?wfVi0*HX61D>Q5`K;WRYSUm-G
-MyKvTnB4D#`vVA~o7aoAYAVxF>R;EEp*j1ts(Ei@!SxWuY)$KQjDp%lOj;vsS;$)b^6WFzPB2W-VtH
%bzGWjRi^okaVTJI=L}R$swpN2trBMuADdCX~TYACbjk*5a^MQMOdIhpmJ|WdMJJ^rGQfgV$|^!b3>Y
u7Z<*4=?kuJ$>UC9c<cie6={gPCD+d&KD2ekB5s#?#H9W^|j-+t4j#giE#JZ#kv2R==5U*#77HuG)Vp
QD+Q@hOuEKmyk9xE60Ed0()~c$F~pI7IvNm9;_#LGyvoZK;+ofRG8-;;{2c@U<Zve|_|~<dsEI+*zIi
H0f3>hSCCl=`N}v*<5G=q@jkUv7E1@*xLzHP4wT6ED5g5hM&z049y$97)!|kvH^^gH~s?&PU<WS3^cU
Q^CF04`5NHhwB#7B^?vFA!X1ly*m&Eo8A101!h6b_%&`<kCY&OejJKzVxh_w#=|I<&B>Xxz|~LdJ{n{
1j-%^Z|6Y9{-V`?v$XsZgx7i|B;EhOaz_>y{qtZP~zrEnVnDAq0+J3L}LM$pdMFym!JSs1`*PxJm4b^
f*HonQ4gf_!HH>VrcNUD!{XczuK^ulMD4_L<w?vnLKAHl4pFjE-xIPmP4F~fg9yf*6nQ^*4$e>F!-n<
<<xZh!G}oRTf!}uQApKN)0M-me7E|TnQ{_5W&`FG6M^{tt)8B=GRpEHhG)Inyr1gb+JS-(dpjV{dW0z
ll`89C3Q&1MzcF;0WD)qjt@k)rwpD)k<I>6Xd*{!Vho#hFRJyf5-_;IMy{QI!;vFkce=f6i;yJIogPw
?m(E+Lk_QqA*SUD5<x6c<`6-RGOh3xCc{{=9G~Qz*&c@W_@Kg)0D2+Emp9mFlOG?YxsHb_PSi%lq`Sz
wqOT@570Isvr1<CAn#99L0hsV|9`ENFg|0@{K(@C9yP3yD;iqKS<1AZo~;ZNQ?WDLi2^3E<R$_mDn2k
1|_3AI9TwwF-8<WSE$|C^o_(l8tdB$D*g2as9n7X>5i&BJ0o4UKo0thfuf=83a_6v>ATxt@7OqRO#Q)
RZxqarjvIeGoQ>V)FaLpq_GJJCwOdDKVPNw|b%$MF7hU`oF%FL=EV2rW680Criux}H1kZ{n#}D9NbTw
^5^%k~*Fa5*3+B59hs3V~swVUJnw++a!p&`2kY~WQ@LLCMCz`mg}ZQ1qKj?Nq0!;FN*Ve3jli)Je!k2
_l5b^~v406}d!0AZAaYuzke(ldd*ZHMa;n3MQWrGFyW<Eq--3YPHUiKWT)!(g2p`Zr8Z4lUK~-HqLO?
fe3ZkhYTFw<2X1=_Y0ASr_&E=Dbiph>FGxy$j=&wkY==JD|+^uCMRm0OqswGl*}v2`mD&c%-4josPLx
9JMX3kAOT0f`x(~C5-$Sto`icMJ&xbfiXL;rp9I^U|AFp8jJMcISiVQeFQ_Xw0i_Y_Cbu;haJ=}-9S&
<i;qldI$)mm%};X5d+ZHaerLs~xNZ_c&y0QzFaBNU$8p6wF0Os@Cd=nApd4v7mWR*S<DfV4dk3q#P9X
L>J>ISY8yPyUfT-IVFqdUQMjE|8EH|x-EbYVh*ikeOPTF?@CSL@Ys9+(q$f^~=hHb7!qM_?jx{m#6d4
!$A3+(giv=FOy6Cdp2CwjiApl^m);AaN*XB+O}ANW7iLeVsEp@bdSK^iA77a)KdVmTnf2%zPvMVqC07
+_1IWD=3DU#qad2@YW9cNQfQXN5QTNgR62L}zi2eL=yLGM+bSvxBrVuJi4gX!5%eaoDCDz)h<rAR9`l
LVV127>h#kPfGNbeT-!%ggZY70FI$MxPO)$ao#1)L|wyX4tg{UO0oC)NE`%YN56-EK6fScMGZBFS5c3
PRKK_$@7au=Ye7*^HuoV(-&FMCjM7k_j^0_=pDesjSKFrwZHjZli#^Nmou1Hs@V%a8@RCn@@y)Y~m)Y
BA7Z)$GCy$>zy9l+uDb)(fkA1eIH?|7<-pIHHCpxI$AIbLidOswcR5%uhf0O?r$p!50!?#HS;ohERr;
{rdP^JNI_D-x+M}wysBAZH@WjF?-4TlD{-H(C%<E`9V&Fcf}q_XY63aOIi3@bILSZU2_;u5Q=4iKkYH
dt>o&&9e0J%W_r2e=i4-oz{Q1m4<3crszaMm0Ayz)(YRY5li<4zpG*)|a+iGDM#b&el?!<~Qp*e~FH>
f1k$hI77>|;iaFq9(3x*c^ly&;SYGm;b{!}>x`vrWIf>P)L8GA?NIMd#nkmyjK3@qo@(wy#P7VmM}rj
@TK%c6w;WHDU?Va{&jK7q2poqGZ~e+(wC2I4u5##=?GyDollg$yWwPKk12=<o2l}Uhr>Bzs!y1%#N*%
ZjE}bHvu*z-yVq0>;al=g*)V<u*<AYQ}4k0uz$FDR7gH6#ulQT5xBTqi;!j`0}VA)s8@_5M~s$)6Q&P
3z}mOJXYL`GAJDVy}_3=5HXBI(|WJ;w1UZ2V7f{FIkw#4-X=_Wd_dO9KQH000080QExzQP<=O3tSKY0
3$a503HAU0B~t=FJEbHbY*gGVQepBZ*FF3XLWL6bZKvHE^v9xTYGQYI1>NgpMtBRu#8pI?cU;WYan;m
N7@aVra{xkE_{YovFMl^SrSM&i7&`~_L~`!5-G_}ySoRRQM9&14u|vj&4X+Z1TV^BDK0lMtwmX|by}p
Ce9eoRDPC`?(dfKfb5?V?7Dbttm)q&+fEDSQj~IKV*o_o*%?l<9wje@mDRQo27<8TH8yxis|7EFC<wB
%2&)AKqS1i>;4%ijn!k|<50Tk93qOc=GJyyWPg7^x}ml$VFh`JPMQ6m>jiQ+Qn?530%%eY!d0c0-O&5
BE4eZ>uHc8{>)0Wrs_R7keKrI)f?kAff=jl{YtWzF((k><Spb$JOS?axx#Z)&SXBb>}CQN_tMFS1g`O
5Dcl@|r7VhG_<>