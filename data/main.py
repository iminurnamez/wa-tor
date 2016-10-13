from . import prepare,tools
from .states import title_screen, sim_setup, gameplay

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"TITLE": title_screen.TitleScreen(),
                   "SIM_SETUP": sim_setup.SimSetup(),
                   "GAMEPLAY": gameplay.Gameplay()}
    controller.setup_states(states, "TITLE")
    controller.main()
