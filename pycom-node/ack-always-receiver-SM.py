    Not All- & w=expected +---+   +---+w = Not expected
    ~~~~~~~~~~~~~~~~~~~~~ |   |   |   |~~~~~~~~~~~~~~~~
    Set lcl_bm(FCN)       |   v   v   |discard
                         ++===+===+===+=+
   +---------------------+     Rcv      +--->* ABORT
   |  +------------------+   Window     |
   |  |                  +=====+==+=====+
   |  |       All-0 & w=expect |  ^ w =next & not-All
   |  |     ~~~~~~~~~~~~~~~~~~ |  |~~~~~~~~~~~~~~~~~~~~~
   |  |    set lcl_bm(FCN)     |  |expected = next window
   |  |      send lcl_bm       |  |Clear lcl_bm
   |  |                        |  |
   |  | w=expected & not-All   |  |
   |  | ~~~~~~~~~~~~~~~~~~     |  |
   |  |     set lcl_bm(FCN)+-+ |  | +--+ w=next & All-0
   |  |     if lcl_bm full | | |  | |  | ~~~~~~~~~~~~~~~
   |  |     send lcl_bm    | | |  | |  | expected = nxt wnd
   |  |                    v | v  | |  | Clear lcl_bm
   |  |w=expected& All-1 +=+=+=+==+=++ | set lcl_bm(FCN)
   |  |  ~~~~~~~~~~~  +->+    Wait   +<+ send lcl_bm
   |  |    discard    +--|    Next   |
   |  | All-0  +---------+  Window   +--->* ABORT
   |  | ~~~~~  +-------->+========+=++
   |  | snd lcl_bm  All-1 & w=next| |  All-1 & w=nxt
   |  |                & MIC wrong| |  & MIC right
   |  |          ~~~~~~~~~~~~~~~~~| | ~~~~~~~~~~~~~~~~~~
   |  |            set lcl_bm(FCN)| |set lcl_bm(FCN)
   |  |                send lcl_bm| |send lcl_bm
   |  |                           | +----------------------+
   |  |All-1 & w=expected         |                        |
   |  |& MIC wrong                v   +---+ w=expected &   |
   |  |~~~~~~~~~~~~~~~~~~~~  +====+=====+ | MIC wrong      |
   |  |set lcl_bm(FCN)       |          +<+ ~~~~~~~~~~~~~~ |
   |  |send lcl_bm           | Wait End |   set lcl_bm(FCN)|
   |  +--------------------->+          +--->* ABORT       |
   |                         +===+====+=+-+ All-1&MIC wrong|
   |                             |    ^   | ~~~~~~~~~~~~~~~|
   |      w=expected & MIC right |    +---+   send lcl_bm  |
   |      ~~~~~~~~~~~~~~~~~~~~~~ |                         |
   |       set lcl_bm(FCN)       | +-+ Not All-1           |
   |        send lcl_bm          | | | ~~~~~~~~~           |
   |                             | | |  discard            |
   |All-1&w=expected & MIC right | | |                     |
   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~ v | v +----+All-1         |
   |set lcl_bm(FCN)            +=+=+=+=+==+ |~~~~~~~~~     |
   |send lcl_bm                |          +<+Send lcl_bm   |
   +-------------------------->+    END   |                |
                               +==========+<---------------+
          --->* ABORT
               ~~~~~~~
               Inactivity_Timer = expires
           When DWL
             IF Inactivity_Timer expires
                Send DWL Request
                Attempt++
