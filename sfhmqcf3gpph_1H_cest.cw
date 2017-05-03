;sfhmqcf3gpph_1H_cest.cw
;
;SOFAST HMQC with 1H saturation (and 15N decoupling) during recycle period
;
;2D H-1/X correlation via heteronuclear zero and double quantum
;   coherence
;phase sensitive
;with decoupling during acquisition
;
;P.Schanda and B. Brutscher, J. Am. Chem. Soc. 127, 8014 (2005)
;
;$CLASS=HighRes
;$DIM=2D
;$TYPE=
;$SUBTYPE=
;$COMMENT=


prosol relations=<triple>


#include <Avance.incl>
#include <Grad.incl>
#include <Delay.incl>


define list<frequency> H1sat = <$FQ1LIST>


"d11=30m"
"d12=20u"
"d21=1s/(cnst4*2)"


"in0=inf2"

"d0=in0/2-p21*4/3.1415"


"DELTA1=d21-p16-d16-p39*cnst39"
"DELTA2=p39*cnst39-4u"
"acqt0=0"


"spoff23=bf1*(cnst19/1000000)-o1"
"spoff24=bf1*(cnst19/1000000)-o1"


; to prevent cross-talk between saturation points, record full planes sequentially
aqseq 321


1 ze 
  d11 pl26:f3
2 d1 do:f3

  ; CEST period
  4u pl8:f1 pl26:f3
  4u H1sat:f1
  4u; LOCKH_ON
  d18 cw:f1 ph1 ;cpd3:f3
  4u do:f1 do:f3
  4u; LOCKH_OFF

  4u pl1:f1 pl3:f3
  4u fq=0:f1

  ; purge
  50u UNBLKGRAD

  p16:gp2
  d16

  ; start HMQC
  (p39:sp23 ph1):f1
  p16:gp1
  d16

 (center (p40:sp24 ph2):f1 (DELTA1 p21 ph3 d0 p21 ph4 DELTA1):f3 )

  DELTA2
  p16:gp1
  d16 pl26:f3
  4u BLKGRAD
  go=2 ph31 cpd3:f3 
  d1 do:f3 mc #0 to 2 
     F2PH(ip3, id0)
     F1QF(rp3 & rd0 & H1sat.inc)
exit 
  

ph1=0 
ph2=0 
ph3=0 2
ph4=0 0 2 2 
ph31=0 2 2 0


;pl3 : f3 channel - power level for pulse (default)
;pl26: f3 channel - power level for CPD/BB decoupling (low power)
;sp23: f1 channel - shaped pulse 120 degree 
;                   (Pc9_4_120.1000)
;sp24: f1 channel - shaped pulse 180 degree (Rsnob.1000)
;p16: homospoil/gradient pulse                       [1 msec]
;p21: f3 channel -  90 degree high power pulse
;p39: f1 channel - 120 degree shaped pulse for excitation
;                      Pc9_4_120.1000 (120o)    (3.0ms at 600.13 MHz)
;p40: f1 channel - 180 degree shaped pulse for refocussing
;                      Rsnob.1000               (1.0ms at 600.13 MHz)
;d0 : incremented delay (2D) = in0/2-p21*4/3.1415
;d1 : relaxation delay (excluding saturation time)
;d11: delay for disk I/O                             [30 msec]
;d12: delay for power switching                      [20 usec]
;d16: delay for homospoil/gradient recovery
;d18: saturation time
;pl8: f1 channel - power level for CEST saturation
;d21 : 1/(2J)NH
;cnst4: = J(NH)
;cnst19: H(N) chemical shift (offset, in ppm)
;cnst39: compensation of chemical shift evolution during p39
;           Pc9_4_120.1000: 0.529
;inf1: 1/SW(N) = 2 * DW(N)
;in0: 1/ SW(N) = 2 * DW(N)
;nd0: 1
;ns: 2 * n
;ds: 16
;aq: <= 50 msec
;td1: number of experiments
;FnMODE: States-TPPI, TPPI, States or QSEC
;cpd3: decoupling according to sequence defined by cpdprg3: garp4.p62
;pcpd3: f3 channel - 90 degree pulse for decoupling sequence
;          use pulse of >= 350 usec


;use gradient ratio:	gp 1 : gp 2
;			  11 :    7


;for z-only gradients:
;gpz1: 11%
;gpz2:  7%

;use gradient files:   
;gpnam1: SMSQ10.100
;gpnam2: SMSQ10.100


                                          ;preprocessor-flags-start
;LABEL_CN: for C-13 and N-15 labeled samples start experiment with
;             option -DLABEL_CN (eda: ZGOPTNS)
                                          ;preprocessor-flags-end


;Processing

;PHC0(F1): 90
;PHC1(F1): -180
;FCOR(F1): 1



;$Id: sfhmqcf3gpph,v 1.10.6.2 2013/03/08 15:13:06 ber Exp $
