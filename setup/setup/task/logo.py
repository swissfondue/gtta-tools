# coding: utf8

from setup.task import Task

_GTTA_LOGO = """
                                            ./+-`
                                        `-ohho+yhs/.
                                    `./yhy/.    `:ohyo-`
                                 `:ohh+-`           ./yhs/.`
                                +ms/.        ````      `-omh    ........` ........`   ....`
                                sM`       `+hdmmds.       hm   -NNNNNNNN+.NNNNNNNNo  :NNNNy
                                sM`       yMMd:yMMd       hm   `//dMMN//-`//hMMM//-  hMMdMM.
                                sM`      `NMM'            hm      yMMm      sMMN    :MMd/MMy
                                sM`      .MMM  mmmm       hm      yMMm      sMMN    hMMo.NMM-
                                sM`      .NMM...MMM       hm      yMMm      sMMN   :MMMNmMMMy
                                sM`       yMMmohMMM       hm      yMMm      sMMN   hMMh--+MMM.
                                oM:`      `+yhhs'ss     `-dm      :++/      -+++  `+++-  `+++-
                                `/shy+-              ./shy+.
                                   `-+yds:`       -+hho:`
                                       `:shh+-./ydy/.`
                                          `.+yho-`


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
