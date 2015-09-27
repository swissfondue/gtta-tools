# coding: utf8

from setup.task import Task

_GTTA_LOGO = """
                                                           ````
                                                       `...`.``.`````
                                                    `...-.--////:::-::-.`.``        ```
                                                   ...:soshhyooosyyhyhyyys+:--`  `..--....`
                                                 `--/yyhhhhhhhhhhhhhhhhhhhhhy+----+hmNMms.-.
                                                `.-+sshhhhhhhhhhhhhhhhhhyyyyyhy+--mMMMMMMh.-.
                                               `--+yhhhhhhhhhhhhhhhso//+osso+//os::hMhdMMM:-.
                                               ..+hhhysooossyhhhhs:/yNMMMMMNmdhs:/:-:dMMMM-..
                                         ` `  .-:hy+/oydddhs/:sho:dMNmhyyhysdmdyyy:-.dMMMs..`
                                        .-/oo:..+//dMMMMMmmNMN+:-Nohhdmmsoyy-:hmdsm:-:dh+..`
                                      `-+NMMMm-..odMMMmdhysssyhohysmmmmh`ydy/./mmd+y-....`
                                     ..oMMMMMN---Nohhooo/sdmmmmmddmmmdmm/-.-+/hyyhym..`
                                     .-NMMMdys-./N/m/smms::mmdhhhhssyyhdhs++yydMMMMm..
                                     .-NMMNNMMy.-N+h:-::+-:dyomdsyNMMydMMMMMMMMMMMM/..
                                     `-yMMMMMMM/.+msds//:/sssMMmhNMMMNMMMMMMMMMMNh:.-
                                      .-smMNmds:.-+h+oohmMMMMMMMMMMMNMmhmmmmmmmdo..`
                                       `.---:--``---omMMMMMMMMMMmhhmNMhmMMMMMd+...
                                                  `.-:ohNMMMMMMMMMMdhhNNhdy+-..`
                                           `--://:-``..-.-:-oyhdddddhyo/--.``
                                        `-ohhyyyyhhhs+: .`-+/:----::/++shhs-`    ```
                                       `ohy+``    `.+yy+`-yhhhohhhhhhhhhhhhs:``.---....
                                      .yhy.`     ``.-:`..oshhhhohhhhhyhshhhho:.-yhhhyo-.
                                     -yhy.     `.:+yho--ohhhhhh+syhhh/+yhhhhhh/.-yhhhho-`
                                    .yhh-`    .`+hhhy:-+hhhhhhho:ohhh./hhhhhhhh-./hhhho-.
                                   `yhh:      .`:hhh+./hhhhhhhhy./hh/`shhhhhhhh/.-hhhy:-`
                                  `yhho`      ..`/yh:.+hhhhhhhhh/-hs`:hhhhhhhhh:./sso--`
                                 `yhhy-      `..-`..-..:+oyyyyyy+.+..shhhhhhyo:`-:-..:-`
                                .yhhhs.    -/osooso+..::-.....--:::-.------..---/+oshyoo/-`
                               -yhhhhy`    `..//:os-.:::oys/yy/-//:-+o::oy/++/::.-/+-/s+--`
                              -yhhhhhh`     ```.:-` ``.++:-:o-. `` `````.:/..-:.``..--````
                             .yhhhhhhh.               ``` ````            ``
                            .yhhhhhhhh/        `````   `````       `.--.```  `````   `````
                           `yhhhhhhhhhy`       yhhhh   shhhh:   `+yhhhhhhy- .yhhhy`.ohhhh-
                           ``:+shhhhhhh+       yhhhh   shhhh:  -hhhhhsooos-  .yhhhyyhhhh-
                               ` ./shhhh+      yhhhh   shhhh:  /hhhhy-` ``.   .yhhhhhhh-
                                    `-/shs-    shhhhs++hhhhh:  .shhhhhhhhy-    .hhhhhh:
                                        `:oo+-``/syso/.+ssss-    -/ossssso-   `-hhhhh:
                                            `:oo/-.`                 `        :hhhhh/`
                                                ./oooo+++++oooooo+++++++++oso+yhhhh+
                                                                          ..`      `

                         GTTA IS NOW READY TO USE. PLEASE CONTINUE YOUR CONFIGURATION IN THE WEB BROWSER.
                                             PRESS ENTER TO GO BACK TO THE MAIN MENU
"""


class Logo(Task):
    """Post-install info"""
    NAME = None
    DESCRIPTION = None

    def main_automatic(self):
        """Main automatic task function"""
        self._show_logo()

    def main(self):
        """Main task function"""
        self._show_logo()

    def _show_logo(self):
        """Show logo"""
        if self.automatic:
            print "\n"

        print _GTTA_LOGO

        try:
            raw_input("Press enter to continue...")
        except KeyboardInterrupt:
            pass

        self.changed = True
