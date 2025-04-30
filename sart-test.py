from psychopy import visual, core, event, data, gui
import random
import os
from datetime import datetime

# ===== Experiment Settings =====
n_trials = 100
practice_trials = 10
digit_duration = 0.250
mask_duration = 0.900
target_probability = 0.11
digit_size = 150
instruction_size = 50
feedback_size = 60
end_text_size = 50
probe_font_size = 50
probe_interval = 20
font_size_options = [48, 72, 94, 100, 120]

# ===== Setup Experiment Info Dialog with PID validation =====
while True:
    exp_info = {
        'PID': '',
        'session': ['1', '2', '3', '4', '5', '6'],
    }
    dlg = gui.DlgFromDict(dictionary=exp_info, title='SART Task')
    if not dlg.OK:
        core.quit()
    if (len(exp_info['PID']) == 9 and exp_info['PID'][0].lower() == 'a' and exp_info['PID'][1:].isdigit()):
        break
    else:
        print("Error: Please enter a valid PID.")

# ===== Initialize Window =====
win = visual.Window(
    fullscr=True, color=[-1, -1, -1], units='norm', allowGUI=False
)

exp_info['date'] = datetime.now().strftime('%Y-%m-%d')
exp_info['time'] = datetime.now().strftime('%H:%M:%S')

# ===== Fixed Target Digit =====
target_digit = 3
exp_info['target_digit'] = target_digit

# ===== Setup Data File =====
data_path = os.path.join(os.getcwd(), 'data')
os.makedirs(data_path, exist_ok=True)
file_name = f"SART_{exp_info['PID']}_{exp_info['session']}_{exp_info['date']}"
exp_handler = data.ExperimentHandler(
    name='SART',
    extraInfo=exp_info,
    dataFileName=os.path.join(data_path, file_name)
)

# ===== Create Stimuli =====
digit_stim = visual.TextStim(win=win, color=[1, 1, 1], height=0.25, font='Arial')
fixation = visual.TextStim(win=win, text='+', color=[1, 1, 1], height=0.1)
feedback_text = visual.TextStim(win=win, color=[1, 1, 1], height=0.15, wrapWidth=1.5)
end_text_stim = visual.TextStim(win=win, color='white', height=0.1, wrapWidth=1.5, font='Arial')

# ===== Helper to make full-screen images =====
def full_screen_image(image_path):
    return visual.ImageStim(win=win, image=image_path, size=(2, 2))

instruction_image = full_screen_image('sart_instructions.png')
probe1_image = full_screen_image('sart_probe1.png')
probe2_image = full_screen_image('sart_probe2.png')
continue_image = full_screen_image('sart_continue.png')

# ===== Texts =====
end_practice_text = f"""
Practice complete!

Reminder:
If digit == {target_digit}, do NOT press anything
Else, press SPACE

Press SPACE to start the test.
"""

end_text = """
Thank you! 

The test is now complete.

Press SPACE to exit.
"""

# ===== Escape Key Handling =====
def quit_save():
    exp_handler.saveAsWideText(exp_handler.dataFileName)
    exp_handler.saveAsPickle(exp_handler.dataFileName)
    win.close()
    core.quit()

# Bind ESC key
event.globalKeys.clear()
event.globalKeys.add(key='escape', func=quit_save)

# ===== Show Probe (Image-Based) =====
def show_probe(image_stim):
    image_stim.draw()
    win.flip()
    keys = event.waitKeys(keyList=['1','2','3','4','5','6'])
    return keys[0] if keys else None

# ===== Show Continue Screen =====
def show_continue(image_stim):
    image_stim.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# ===== Trial Runner =====
def run_block(num_trials, is_practice=False):
    go_correct = go_omissions = nogo_correct = nogo_commissions = 0
    reaction_times = []

    n_targets = int(num_trials * target_probability)
    n_non_targets = num_trials - n_targets

    trial_digits = [target_digit] * n_targets
    non_target_digits_cycle = (list(range(10)) * ((n_non_targets // 9) + 1))
    non_target_digits_cycle = [d for d in non_target_digits_cycle if d != target_digit]
    random.shuffle(non_target_digits_cycle)
    trial_digits += non_target_digits_cycle[:n_non_targets]
    random.shuffle(trial_digits)

    for trial_idx, current_digit in enumerate(trial_digits):
        if not is_practice and trial_idx > 0 and trial_idx % probe_interval == 0:
            attention = show_probe(probe1_image)
            awareness = show_probe(probe2_image)
            show_continue(continue_image)
            exp_handler.addData('probe_trial', trial_idx)
            exp_handler.addData('attention_rating', attention)
            exp_handler.addData('awareness_rating', awareness)
            exp_handler.nextEntry()

        response, rt = None, None
        digit_stim.setText(str(current_digit))
        digit_stim.height = random.choice([0.2, 0.3, 0.4])

        fixation.draw()
        win.flip()
        core.wait(0.5)

        digit_stim.draw()
        win.flip()
        trial_clock = core.Clock()
        keys = event.waitKeys(maxWait=digit_duration, keyList=['space'])
        win.flip()

        if not keys:
            keys = event.waitKeys(maxWait=mask_duration, keyList=['space'])

        if keys:
            response = 'space'
            rt = trial_clock.getTime()

        is_target = (current_digit == target_digit)
        correct = False

        if is_target:
            correct = response is None
            nogo_correct += int(correct)
            nogo_commissions += int(not correct)
        else:
            correct = response == 'space'
            go_correct += int(correct)
            go_omissions += int(not correct)
            if correct:
                reaction_times.append(rt)

        if is_practice and trial_idx < num_trials - 1:
            if is_target:
                msg, col = (f"Correct! You did not respond to {target_digit}.", 'green') if correct else (f"Incorrect. Do not respond to {target_digit}.", 'red')
            else:
                msg, col = ("Correct! You responded.", 'green') if correct else (f"Incorrect. Please press SPACE when the digit is not {target_digit}.", 'red')
            feedback_text.setText(msg)
            feedback_text.setColor(col)
            feedback_text.draw()
            win.flip()
            core.wait(1.5)

        exp_handler.addData('trial', trial_idx + 1)
        exp_handler.addData('digit', current_digit)
        exp_handler.addData('is_target', is_target)
        exp_handler.addData('response', response)
        exp_handler.addData('rt', rt)
        exp_handler.addData('correct', correct)
        exp_handler.nextEntry()

    performance = {
        'go_accuracy': go_correct / (go_correct + go_omissions) if (go_correct + go_omissions) else 0,
        'nogo_accuracy': nogo_correct / (nogo_correct + nogo_commissions) if (nogo_correct + nogo_commissions) else 0,
        'mean_rt': sum(reaction_times) / len(reaction_times) if reaction_times else 0,
    }
    return performance

# ===== Run the Experiment =====

instruction_image.draw()
win.flip()
event.waitKeys(keyList=['space'])

run_block(practice_trials, is_practice=True)

end_text_stim.setText(end_practice_text)
end_text_stim.draw()
win.flip()
event.waitKeys(keyList=['space'])

performance = run_block(n_trials)

for key, value in performance.items():
    exp_handler.addData(f'summary_{key}', value)

end_text_stim.setText(end_text)
end_text_stim.draw()
win.flip()
event.waitKeys(keyList=['space'])

quit_save()
