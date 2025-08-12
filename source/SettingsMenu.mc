using Toybox.WatchUi as Ui;
using Toybox.System as Sys;

// Simple settings menu for feature flag toggles (Issue #9 AC7)
class SettingsMenu extends Ui.Menu2 {
    function initialize() {
        Menu2.initialize({:title=>"Settings"});
        
        // Sleep toggle
        addItem(new Ui.ToggleMenuItem(
            "Sleep Tracking",
            {:enabled=>"On", :disabled=>"Off"},
            :sleep,
            Sys.getApp().getProperty("enableSleep") != null ? Sys.getApp().getProperty("enableSleep") : false,
            {}
        ));
        
        // Stress toggle  
        addItem(new Ui.ToggleMenuItem(
            "Stress Tracking", 
            {:enabled=>"On", :disabled=>"Off"},
            :stress,
            Sys.getApp().getProperty("enableStress") != null ? Sys.getApp().getProperty("enableStress") : false,
            {}
        ));
        
        // HRV toggle
        addItem(new Ui.ToggleMenuItem(
            "HRV Tracking",
            {:enabled=>"On", :disabled=>"Off"}, 
            :hrv,
            Sys.getApp().getProperty("enableHRV") != null ? Sys.getApp().getProperty("enableHRV") : false,
            {}
        ));
    }
    
    function onSelect(item) {
        var id = item.getId();
        var enabled = item.isEnabled();
        
        if (id == :sleep) {
            Sys.getApp().setProperty("enableSleep", enabled);
            ScoreEngine.ENABLE_SLEEP = enabled;
        } else if (id == :stress) {
            Sys.getApp().setProperty("enableStress", enabled);
            ScoreEngine.ENABLE_STRESS = enabled;
        } else if (id == :hrv) {
            Sys.getApp().setProperty("enableHRV", enabled);
            ScoreEngine.ENABLE_HRV = enabled;
        }
    }
}
