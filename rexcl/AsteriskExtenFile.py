
from string import Template
from Parser import Parser
__conf_init__ = """
[dial_icom]
; ARG1 -> icom_name
; ARG2 -> icom_no
; ARG3 -> rly_no
exten => s, 1, Set(CALLERID(all)=${CLI_ICOM})
  same => n(common), Set(REDIR=${DB(${ARG1}-redir/${ARG2})})
  same => n, GotoIf($[${ISNULL(${REDIR})}]?internal:redir)
  same => n(internal), Dial(SIP/${ARG3},60,tT)
  same => n, Hangup
  same => n(redir), Goto(${REDIR},common)


[dial_rly_remote]
; ARG1 -> rly_no
; ARG2 -> sip1
; ARG3 -> sip2
; ARG4 -> Local STD CODE for CLI
exten => s, 1, Set(CALLERID(all)=${ARG4}${CLI_RLY})
  same => n, Set(STATUS=${SIPPEER(${ARG1},status)})
  same => n, GotoIf($[ ${STATUS} = UNREACHABLE]?try2)
  same => n, Dial(SIP/${ARG2}/${ARG1},60, tT)
  same => n, Hangup
  same => n(try2), Dial(SIP/${ARG3}/${ARG1}, 60, tT)
  same => n, Hangup

[dial_byte_remote]
; ARG1 -> rly_no
; ARG2 -> sip1
; ARG3 -> sip2
exten => s, 1, Set(STATUS=${SIPPEER(${ARG1},status)})
  same => n, GotoIf($[ ${STATUS} = UNREACHABLE]?try2)
  same => n, Dial(SIP/${ARG2}/byte-${ARG1},60, tT)
  same => n, Hangup
  same => n(try2), Dial(SIP/${ARG3}/byte-${ARG1}, 60, tT)
  same => n, Hangup

[dial_rly_local]
; ARG1 -> rly_no
; ARG2 -> secy_no
; ARG3 -> secy_type
; ARG4 -> Should i modify CLI:(yes|no)
; ARG5-8 -> Parallel Numbers
; ARG9 -> recording:(yes|no)
  exten => s,1, GotoIf($[${ARG4} = no ] ?noclimod)
  same => n(noclimod), NoOp(Check for Blacklisting)
 ; same => n, GotoIf($["${DB(blist/${CALLERID(num)})}"="${ARG1}"]?bl) ;To check The blocklist
  same => n, GotoIf($["${ARG6}" != "Yes" ] ?norec)
  same => n,Progress()
  same => n,Set(CURRENT_DATE=${STRFTIME(${EPOCH},,%Y.%m.%d)}) ; Get current date in YYYY.MM.DD format
  same => n,Set(CURRENT_TIME=${STRFTIME(${EPOCH},,%H:%M:%S)}) ; Get current time in HH:MM:SS format
  same => n,MixMonitor(rec_${ARG1}_${CALLERID(num)}_${CURRENT_DATE}_${CURRENT_TIME}.wav,aB)
  same => n(norec), Set(REDIR=${DB(rly-redir/${ARG1})})
  same => n, GotoIf($[ "${REDIR}X" != "X"]?redir)
  same => n, GotoIf($["${ARG2}X" = "X"]?nosecy)
  same => n, GotoIf($[${CALLERID(num)} = ${ARG2}]?nosecy)
  same => n, GotoIf($[${ARG3}=only_secy]?only_secy)
  same => n, Dial(SIP/${ARG2},15,tT)
  same => n(nosecy), GotoIf($["${ARG5}X" != "X"]?parallel1)
  same => n, Dial(SIP/${ARG1},60,tT)
  same => n, Voicemail(${ARG1}@rexcs,u)
  same => n, Hangup
  same => n(parallel1),GotoIf($["${ARG6}X" != "X"]?parallel2)
  same => n, Dial(SIP/${ARG1} & SIP/${ARG5},60,tT)
  same => n, Voicemail(${ARG1}@rexcs,u)
  same => n, Hangup
  same => n(parallel2),GotoIf($["${ARG7}X" != "X"]?parallel3)
  same => n, Dial(SIP/${ARG1} & SIP/${ARG5} & SIP/${ARG6},60,tT)
  same => n, Voicemail(${ARG1}@rexcs,u)
  same => n, Hangup
  same => n(parallel3),GotoIf($["${ARG8}X" != "X"]?parallel4)
  same => n, Dial(SIP/${ARG1} & SIP/${ARG5} & SIP/${ARG6} & SIP/${ARG7},60,tT)
  same => n, Voicemail(${ARG1}@rexcs,u)
  same => n, Hangup
  same => n(parallel4), Dial(SIP/${ARG1} & SIP/${ARG5} & SIP/${ARG6} & SIP/${ARG7} & SIP/${ARG8},60,tT)
  same => n, Voicemail(${ARG1}@rexcs,u)
  same => n, Hangup
  same => n(only_secy), DIal(SIP/${ARG2},60,tT)
  same => n, Hangup
  same => n(redir), Playback(call-forwarding)
  same => n, Goto(rly,${REDIR},1)
;  same => n(bl),Answer()
;  same => n,Playback(rexcsVoice/number-trying-to-call-blacklisted-you)
;  same => n,Hangup



[dial_byte_local]
; ARG1 -> rly_no
exten => s, 1, Set(CALLERID(all)=${CLI_BYTE})
  same => n, Set(REDIR=${DB(byte-redir/${ARG1})})
  same => n, GotoIf($[ "${REDIR}X" != "X"]?redir)
  same => n, GotoIf($["${ARG2}X" != "X"]?parallel1)                         
  same => n, Dial(SIP/${ARG1},60,tT)                                        
  same => n, Hangup                                                         
  same => n(parallel1),GotoIf($["${ARG3}X" != "X"]?parallel2)                            
  same => n, Dial(SIP/${ARG1} & SIP/${ARG2},60,tT)                          
  same => n, Hangup                                                         
  same => n(parallel2),Dial(SIP/${ARG1} & SIP/${ARG2} & SIP/${ARG3} ,60,tT) 
  same => n, Hangup                                                             
  same => n(redir), Goto(byte-icom,${REDIR})


[change-conf-pin]
;ARG1 -> conference name
;ARG2 -> rly number of admin phone of the conference 
exten => s, 1, Answer
    same => n, Playback(conf-getpin)
    same => n, Read(pin,,4)
    same => n, Set(DB(conf/${ARG1})=${pin})
    same => n, Goto(rly,playpin-${ARG2},1)
    same => n, Hangup

[rly]
;Call forward
exten=> _*72,1,NoOp(Activating Call Forwarding)
    same => n,Read(FORWARD_DESTINATION,telephone-number,5) ; Prompt the user to enter the destination
    same => n,Set(DB(rly-redir/${CALLERID(num)})=${FORWARD_DESTINATION}) ; Store the f>
    same => n,GotoIf($[ "${FORWARD_DESTINATION}X" = "X"]?tryagain)
    same => n,Playback(activated)
    same => n,Hangup
    same => n(tryagain), Playback(please-try-again)
    same => n,Hangup


exten => *73,1,NoOp(${DB_DELETE(rly-redir/${CALLERID(num)})})
    same => n,Playback(de-activated)
    same => n,Hangup

;Byte Call forward
exten=> _*74,1,NoOp(Activating Call Forwarding)
    same => n,Read(FORWARD_DESTINATION,telephone-number) ; Prompt the user to enter the destination
    same => n,Set(DB(byte-redir/${CALLERID(num)})=${FORWARD_DESTINATION}) ; Store the f>
    same => n,GotoIf($[ "${FORWARD_DESTINATION}X" = "X"]?tryagain)
    same => n,Playback(activated)
    same => n,Hangup
    same => n(tryagain), Playback(please-try-again)
    same => n,Hangup


exten => *75,1,NoOp(${DB_DELETE(byte-redir/${CALLERID(num)})})
    same => n,Playback(de-activated)
    same => n,Hangup


;conference admin - play pin.
exten => *260, 1, Set(CALLERID(all)=${CLI_RLY})
    same => n, Set(ADMIN=${CALLERID(num)})
    same => n, Goto(rly,playpin-${ADMIN},1)

;conference admin - set pin.
exten => *261, 1, Set(CALLERID(all)=${CLI_RLY})
    same => n, Set(ADMIN=${CALLERID(num)})
    same => n, Goto(rly,setpin-${ADMIN},1)

exten => *30, 1, CallCompletionRequest
    same => n, Answer(500)
    same => n, Playback(auth-thankyou)
    same => n, Hangup

exten => *31, 1, CallCompletionCancel
    same => n, Answer(500)
    same => n, Playback(auth-thankyou)
    same => n, Hangup

exten => *38, 1, Answer
    same => n, SayUnixTime(,Asia/Kolkata,ABdY \’digits/at\’ IMp)
    same => n, Hangup
    
exten => *100,1,VoiceMailMain(${CALLERID(num)}@rexcs) 

;Code for Blacklisting a number
;exten => *36,1,NoOp(Initiating Call Blacklisting)
;    same => n,Read(blacklist-number,rexcsVoice/enter-number-to-add-to-blacklist) ;Prompt to enter the number which need to added to blacklist.
;    same => n,Playback(beep)
;    same => n,Playback(you-entered)
;    same => n,SayDigits(${blacklist-number})
;    same => n,Set(DB(blist/${blacklist-number})=${CALLERID(num)})
;    same => n,Playback(rexcsVoice/entered-number-added-to-blacklist)
;    same => n,Hangup
    
;Code to delete a number from Blacklist
;exten => *37,1,NoOp(Deleting Extensions from Blacklisting)
;    same => n,Read(bdel-number,rexcsVoice/enter-number-to-delete-from-blacklist) ; Prompt to enter the number which need to be removed from balcklist.
;    same => n,Playback(beep)
;    same => n,Playback(you-entered)
;    same => n,SayDigits(${bdel-number})
;    same => n,NoOp(${DB_DELETE(blist/${bdel-number})}) ; This will delete the number from the blist DB entry
;    same => n,Playback(rexcsVoice/entered-number-deleted-from-blacklist)
;    same => n,HangUp

"""

dial_rly_remote = """
macro dial_rly_remote( rly_no, sip1, sip2) {
  if (${SIPPEER(${sip1}, status)} = UNREACHABLE) {
    if (${sip2} != "") {
      Dial(SIP/${sip2}/${rly_no}, 60, tT);
    }
  } else {
    Dial(SIP/${sip1}/${rly_no}, 60, tT);
  }
};


macro dial_rly_local(rly_no, secy_no) {
    Set(CALLERID(all) = ${CLI_RLY});
common:
    Set(REDIR=${DB(rly-redir/${rly_no})});
    if(${REDIR} = "") {
        if (${secy_no} != "") {
            if (${CALLERID(num)} = ${secy_no}) {
                Dial(SIP/${secy_no}, 60, tT);
            }
        }
        Dial(SIP/${rly_no}, 60, tT);
    }
    goto rly,${REDIR},common;
};


"""

dial_icom = """

macro dial_icom(icom, icom_no, rly_no) {
  Set(CALLERID(all)=${CLI_RLY});
check_redir:
  Set(REDIR=${DB(${icom}-redir/${icom_no})});
  if(REDIR == "") {
    Dial(SIP/${rly_no}, 60, tT);
  } else {
    goto ${redir},check_redir;
  }
};

"""

class AsteriskExtenFile:
    __ael_init = dial_icom + dial_rly_remote
    __conf_init = __conf_init__
    icom_t_old = Template('[icom-$icom]\n'
                      'exten => $icom_no, 1, Set(CALLERID(all)=${CLI_ICOM})\n'
                      '  same => n(common), Set(REDIR=${DB($icom-redir/${EXTEN})})\n'
                      '  same => n, GotoIf($[${ISNULL(${REDIR})}]?internal:redir)\n'
                      '  same => n(internal), Dial(SIP/$rly_no, 60, tT)\n'
                      '  same => n, Hangup\n'
                      '  same => n(redir), Goto(${REDIR}, common)\n\n')

    # icom
    # icom_no
    # rly_no
    __conf_dial_icom_t = Template('exten => $icom_no, 1, GoSub(dial_icom,s,1($icom,$icom_no,$rly_no))\n')
    __conf_hint_icom_t = Template('exten => $icom_no, hint, SIP/$rly_no\n')
    
    # rly_no,
    # sip1
    # sip2
    # rly_std_code
    __conf_dial_rly_remote_t = Template('exten => $rly_no, 1, GoSub(dial_rly_remote,s,1(t$rly_no,$sip1,$sip2,$rly_std_code))\n')

    # rly_no
    # secy_no
    __conf_dial_rly_local_t = Template('exten => $rly_no, 1, GoSub(dial_rly_local,s,1($rly_no,$secy_no,$secy_type,yes,$parallel_num1,$parallel_num2,$parallel_num3,$parallel_num4,$recording))\n' 
                                       'exten => t$rly_no, 1, GoSub(dial_rly_local,s,1($rly_no,$secy_no,$secy_type,no,$parallel_num1,$parallel_num2,$parallel_num3,$parallel_num4,$recording))\n' 
                                       )
    __conf_byte_local_t = Template(
        'exten => byte-$rly_no, 1, GoSub(dial_byte_local,s,1($rly_no,$byte_parallel1,$byte_parallel2))\n') ##23.11.24
    __conf_hint_local_t = Template(
        'exten => $rly_no, hint, SIP/$rly_no\n')
    __conf_byte_remote_t = Template(
        'exten => byte-$rly_no, 1, GoSub(dial_byte_remote,s,1($rly_no,$sip1, $sip2))\n')
    
    __conf_icom_context_t = Template(
        '[icom-$icom-byte]\n'
        'include => icom-$icom\n'
        'include => byte-icom\n\n'
        '[icom-$icom]\n'
        'include => rly\n'
        'include => outgoing\n'
    )
        
    __conf_byte_t = Template('exten => $byte_no, 1, Goto(rly,byte-$rly_no,1)\n') 
    __conf_byte_hint_t = Template('exten => $byte_no, hint, SIP/$rly_no\n') 

    icom_t = Template('exten => $icom_no, 1, GoSub(dial_icom,s,1($icom,$icom_no,$rly_no))\n')
    # AEL templates. 
    __ael_rly_remote_t = Template('  $rly_no => { &dial_rly_remote($rly_no, $sip1, $sip2) };\n')
    __ael_rly_local_t = Template('  $rly_no => { &dial_rly_local($rly_no, $secy_no) };\n') 
    __ael_icom_context_t = Template('context icom-$icom-byte {\n'
                                  '  include {\n'
                                  '    icom-$icom;\n'
                                  '    byte-icom;\n'
                                  '  };\n'
                                  '};\n\n')
    __ael_icom_t = Template('  $icom_no => { &dial_icom($icom, $icom_no, $rly_no) };\n')
        
    # conference template
    # Arguments
    # $conf_no
    # $name
    # $admin_phone_no
    __conf_conference_local_t = Template(
        'exten => $conf_no, 1, Noop\n'
            'same => n, Set(CALLERID(all)=$${CLI_RLY})\n'
            'same => n, Goto(conf-$conf_no,1)\n'
        'exten => t$conf_no, 1, Noop\n'
            'same => n, Goto(conf-$conf_no,1)\n'
        'exten => conf-$conf_no,1,Answer\n'
        '    same => n, Playback(conf-getpin)\n'
        '    same => n, Read(pin,,4)\n'
        '    same => n, Noop($${pin})\n'
        '    same => n, Set(Dbpin=$${DB(conf/snt)})\n'
        '    same => n, GotoIf($$["$${Dbpin}" != ""]?continue)\n'
        '    same => n, Set(Dbpin=0000)\n'
        '    same => n(continue), Noop($${Dbpin})\n'
        '    same => n, GotoIf($$["$${Dbpin}" != "$${pin}"]?error)\n'
        '    same => n, Confbridge($name)\n'
        '    same => n, Hangup\n'
        '    same => n(error), Playback(conf-invalidpin)\n'
        '    same => n, Hangup\n'
        ''
        'exten => playpin-$admin_phone_no, 1, Answer\n'
        '    same => n, Set(PIN=$${DB(conf/snt)})\n'
        '    same => n, SayDigits($${PIN})\n'
        '    same => n, Hangup\n'
        ''
        'exten => setpin-$admin_phone_no, 1, GoSub(change-conf-pin,s,1(snt,$${EXTEN:7}))\n\n')
    
    # $conf_no
    # $sip1
    # $sip2
    __conf_conference_remote_t = Template(
        'exten => $conf_no, 1, Goto(dial_rly_remote,s,1(t$conf_no,$sip1,$sip2, $rly_std_code))\n')
                                          
    
    def __init__(self, reg_lst, phone_lst):
        self.reg_lst = reg_lst
        self.phone_lst = phone_lst
        self.do_conf()
        
    def __write_files(self, f1, f2, c, s):
        # f1 -> main file
        # f2 -> secondary file
        # c -> check variable
        # s -> str to write to file
        # print("c: " + c + ". Str: " + s)
        f1.write(s)
        if (c != ""): f2.write(s)
        
    def __open_files(self, reg, ip_p, ip_s, exten):
        fp_name = reg + '-' + ip_p + '-exten.' + exten
        fp = open(fp_name, 'w') or die ('Cannot open file: ' + fp_name)
        fs_name = ""
        fs = ""
        if (ip_s != ""):
            fs_name = reg + '-b-' + ip_s + '-exten.' + exten
            fs = open(fs_name, 'w') or die ('Cannot open file: ' + fs_name)
        return fp, fs

    def do_conf(self):
        reg_gw_lst = [x for x in self.reg_lst]
        reg_gw_lst += [(x["name"], x["ipv4"], "") for x in Parser._ast["gateway"] ]
        #print(reg_gw_lst)
        for (reg, ip_p, ip_s) in reg_gw_lst:
            fp, fs = self.__open_files(reg, ip_p, ip_s, 'conf')
            self.__write_files(fp, fs, ip_s, self.__conf_init)
            for icom in {x['icom'] for x in self.phone_lst if x['reg'] == reg }:
                self.__write_files(fp, fs, ip_s,
                                   self.__conf_icom_context_t.substitute({
                                       'icom': icom}))
                phs = [x for x in self.phone_lst if x['icom'] == icom]
                
                for ph in phs:
                    s1 = self.__conf_dial_icom_t.substitute({
                        'icom': icom,
                        'icom_no': ph['icom_no'],
                        'rly_no': ph['rly_no']})
                    self.__write_files(fp, fs, ip_s, s1)
                    s1 = self.__conf_hint_icom_t.substitute({
                        'icom_no': ph['icom_no'],
                        'rly_no': ph['rly_no']})
                    self.__write_files(fp, fs, ip_s, s1)
                self.__write_files(fp, fs, ip_s, "\n\n")
                
                # Now generate rly context
            self.__write_files(fp, fs, ip_s, "[rly]\n")
            self.__write_files(fp, fs, ip_s, "include => outgoing\n")
            #print(self.phone_lst)
            for ph in self.phone_lst:
                if ph['reg'] == reg:
                    # Local rly _no
                    s1 = self.__conf_dial_rly_local_t.substitute({
                        'rly_no': ph['rly_no'],
                        'parallel_num1': ph['parallel_num1'],  #new line for parallel phone
                        'parallel_num2': ph['parallel_num2'],  #new line for parallel phone
                        'parallel_num3': ph['parallel_num3'],  #new line for parallel phone
                        'parallel_num4': ph['parallel_num4'],  #new line for parallel phone
                        'recording': ph['recording'],   #new line for recording
                        'secy_type': ph['secy_type'],
                        'secy_no': ph['secy_no']})
                    if Parser._ast['general']['rly-std-code'] != '':
                        s1 += self.__conf_dial_rly_local_t.substitute({
                        'rly_no': Parser._ast['general']['rly-std-code'] + ph['rly_no'],
                        'parallel_num1': ph['parallel_num1'],  #new line for parallel phone
                        'parallel_num2': ph['parallel_num2'],  #new line for parallel phone
                        'parallel_num3': ph['parallel_num3'],  #new line for parallel phone
                        'parallel_num4': ph['parallel_num4'],  #new line for parallel phone
                        'recording': ph['recording'],   #new line for recording
                        'secy_type': ph['secy_type'],
                        'secy_no': ph['secy_no']})
                        
                    if ph["byte_no"] != "":
                        s1 += self.__conf_byte_local_t.substitute({
                            'rly_no': ph["rly_no"],
                            'byte_parallel1': ph['byte_parallel1'],  ###23.11.24
                            'byte_parallel2': ph['byte_parallel2']})  ###23.11.24
                            
                      
                    s1 += self.__conf_hint_local_t.substitute({
                            'rly_no': ph["rly_no"]})
                  
                    self.__write_files(fp, fs, ip_s, s1)
                else:
                    # Remote rly no
                    (r, i, p) = [x for x in self.reg_lst if x[0] == ph["reg"] ][0]
                    sip1 = r
                    sip2 = ""
                    if (p != ''): sip2 = r + '-b'
                    s1 = self.__conf_dial_rly_remote_t.substitute({
                        'rly_no': ph['rly_no'],
                        'sip1': sip1,
                        'sip2': sip2,
                        'rly_std_code': Parser._ast['general']['rly-std-code']})
                    if Parser._ast['general']['rly-std-code'] != '':
                        s1 += self.__conf_dial_rly_remote_t.substitute({
                            'rly_no': Parser._ast['general']['rly-std-code'] + ph['rly_no'],
                            'sip1': sip1,
                            'sip2': sip2,
                            'rly_std_code': Parser._ast['general']['rly-std-code']})
                        
                    if ph["byte_no"] != "":
                        s1 += self.__conf_byte_remote_t.substitute({
                            'rly_no': ph["rly_no"],
                            'sip1': sip1,
                            'sip2': sip2 })
                    self.__write_files(fp, fs, ip_s, s1)
                #end if
            #end for
            self.__write_files(fp, fs, ip_s, "\n\n")
            self.__do_byte(fp, fs, ip_s)
            self.__do_route(reg, fp, fs, ip_s)
            self.__do_conference(reg, fp, fs, ip_s)
            self.__do_map(fp, fs, ip_s)
            fp.close()
            if (fs != ''): fs.close()
                    
    def __do_byte(self, fp, fs, ip_s):
        self.__write_files(fp, fs, ip_s, "[byte-icom]\n")
        byte_phones = [x for x in self.phone_lst if x["byte_no"] != "" ]
        for b in byte_phones:
            s1 = self.__conf_byte_t.substitute({
                'byte_no': b["byte_no"],
                'rly_no': b["rly_no"]})
            self.__write_files(fp, fs, ip_s, s1)
            s1 = self.__conf_byte_hint_t.substitute({
                'byte_no': b["byte_no"],
                'rly_no': b["rly_no"]})
            self.__write_files(fp, fs, ip_s, s1)
        # end for
        self.__write_files(fp, fs, ip_s, "\n\n")
              

    def __do_route(self, reg, fp, fs, ip_s):
        self.__write_files(fp, fs, ip_s, "[outgoing]\n")
        routes  = [x for x in Parser._ast["route"] if x["rname"] == reg]
        for r in routes:
            if r['cli'] == "CLI-RLY":
                s1 = "exten => _" + r['pattern'] + ", 1, Set(CALLERID(all) = ${CLI_RLY})\n"
                s1 += '  same => n, Set(CID=' + Parser._ast['general']['rly-std-code'] + '${CALLERID(num)})\n'
                s1 += '  same => n, Set(CALLERID(num)=${CID})\n'
            elif r['cli'] == "CLI-PSTN":
                s1 = "exten => _" + r['pattern'] + ", 1, Set(CALLERID(all) = ${CLI_PSTN})\n"
                s1 += '  same => n, Set(CID=' + Parser._ast['general']['pstn-std-code'] + '${CALLERID(num)})\n'
                s1 += '  same => n, Set(CALLERID(num)=${CID})\n'
            elif r['cli'] == 'NIL':
                s1 = "exten => _" + r['pattern'] + ", 1, Noop\n"
            for rdef in r['rdef']:
                s1 += '  same => n, Dial(SIP/sip-' + rdef["name"] + '/'
                try:
                    rdef['fname']
                    if rdef['fname'] == "prefix":
                        s1 += rdef['val'] + "${EXTEN}"
                    elif rdef['fname'] == "postfix":
                        s1 += "${EXTEN}" + rdef['val']
                    elif rdef['fname'] == "slice":
                        s1 += "${EXTEN:" + rdef['val'] + "}"
                    #end if
                except:
                    s1 += "${EXTEN}"
                finally:
                    s1 += ", 60, tT)\n"
            s1 += "  same => n, Hangup\n\n"
            self.__write_files(fp, fs, ip_s, s1)
                

    def __do_conference(self, reg, fp, fs, ip_s):
        self.__write_files (fp, fs, ip_s, "; Generating Conference dial plans\n[rly]\n")
        for c in Parser._ast["conference"]:
            if (reg == c["reg"]):
                # This conference is defined in this registrar
                self.__write_files(fp, fs, ip_s,
                                   self.__conf_conference_local_t.substitute(c))
            else:
                sip1 = "sip-" + c["reg"]
                sip2 = ""
                bip = [x for x in Parser._ast["registrar"] if x["name"] == c["reg"]][0]["bip"]
                if bip != "":
                    sip2 = sip1 + "-b"
                self.__write_files(fp, fs, ip_s,
                                   self.__conf_conference_remote_t.substitute(
                                       {'conf_no': c['conf_no'],
                                        'sip1': sip1,
                                        'sip2': sip2,
                                        'rly_std_code': Parser._ast['general']['rly-std-code']}))
   
                
                    
    def __do_map(self, fp, fs, ip_s):
        self.__write_files(fp, fs, ip_s, ";Generating maps \n[rly]\n")
        for m in Parser._ast["map"]:
            rly_no = [x["rly_no"] for x in Parser._ast['phone'] if x["name"] == m["phone"] ][0]
            s1 = "exten => " + m["short_code"] + ", 1, Goto(rly," + rly_no + ",1)\n"
            self.__write_files(fp, fs, ip_s, s1)
        
