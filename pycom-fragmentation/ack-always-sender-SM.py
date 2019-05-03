
                 +=======+
                 | INIT  |       FCN!=0 & more frags
                 |       |       ~~~~~~~~~~~~~~~~~~~~~~
                 +======++  +--+ send Window + frag(FCN)
                    W=0 |   |  | FCN-
     Clear lcl_bm       |   |  v set lcl_bm
          FCN=max value |  ++==+========+
                        +> |            |
   +---------------------> |    SEND    |
   |                       +==+===+=====+
   |      FCN==0 & more frags |   | last frag
   |    ~~~~~~~~~~~~~~~~~~~~~ |   | ~~~~~~~~~~~~~~~
   |               set lcl_bm |   | set lcl_bm
   |   send wnd + frag(all-0) |   | send wnd+frag(all-1)+MIC
   |       set Retrans_Timer  |   | set Retrans_Timer
   |                          |   |
   |Recv_wnd == wnd &         |   |
   |lcl_bm==recv_bm &         |   |  +----------------------+
   |more frag                 |   |  | lcl_bm!=rcv-bm       |
   |~~~~~~~~~~~~~~~~~~~~~~    |   |  | ~~~~~~~~~            |
   |Stop Retrans_Timer        |   |  | Attempt++            v
   |clear lcl_bm              v   v  |                +=====+=+
   |window=next_window   +====+===+==+===+            |Resend |
   +---------------------+               |            |Missing|
                    +----+     Wait      |            |Frag   |
   not expected wnd |    |    Bitmap     |            +=======+
   ~~~~~~~~~~~~~~~~ +--->+               ++Retrans_Timer Exp  |
       discard frag      +==+=+===+=+==+=+| ~~~~~~~~~~~~~~~~~ |
                            | |   | ^  ^  |reSend(empty)All-* |
                            | |   | |  |  |Set Retrans_Timer  |
                            | |   | |  +--+Attempt++          |
   MIC_bit==1 &             | |   | +-------------------------+
   Recv_window==window &    | |   |   all missing frags sent
                no more frag| |   |   ~~~~~~~~~~~~~~~~~~~~~~
    ~~~~~~~~~~~~~~~~~~~~~~~~| |   |   Set Retrans_Timer
          Stop Retrans_Timer| |   |
    +=============+         | |   |
    |     END     +<--------+ |   |
    +=============+           |   | Attempt > MAX_ACK_REQUESTS
               All-1 Window & |   | ~~~~~~~~~~~~~~~~~~
                MIC_bit ==0 & |   v Send Abort
             lcl_bm==recv_bm  | +=+===========+
                 ~~~~~~~~~~~~ +>|    ERROR    |
                   Send Abort   +=============+



          Figure 40: Sender State Machine for the ACK-Always Mode