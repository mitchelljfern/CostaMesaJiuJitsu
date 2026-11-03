#!/usr/bin/env python3
"""Builds the draft /waiver/ page (saved on the waiver-draft branch until January).

Usage: python3 waiver.py <repo-dir> <old-pages-dir>
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO, OLD = sys.argv[1:3]
src = open(os.path.join(HERE, 'build.py'), encoding='utf-8').read()
exec(compile(src.split('# ================================================================ /free-trial/')[0], 'build.py', 'exec'))

GYM = 'Costa Mesa Jiu Jitsu'
RELEASED = 'Costa Mesa Jiu Jitsu, Double Ops, and their owners, coaches, instructors, employees, volunteers and landlord (together, "the Gym")'

waiver_text = f'''
<h2>Release of Liability, Assumption of Risk and Agreement Not to Sue</h2>
<p>Please read this carefully. By signing, you give up legal rights, including the right to sue.</p>

<h3>1. Activities</h3>
<p>This waiver covers all classes, open mats, private lessons, events, competitions and any other use of the facility or equipment at {GYM}, including Brazilian jiu jitsu (Gi and NoGi), grappling, striking, kickboxing, boxing, conditioning, strength training and related activities ("the Activities").</p>

<h3>2. I understand the risks</h3>
<p>Martial arts and fitness training are physical contact activities. I understand the Activities carry risks of injury, including but not limited to sprains, strains, cuts, bruises, dislocations, broken bones, concussions, joint and spinal injuries, infections, heart attack, paralysis and death. These risks can come from my own actions, the actions of training partners, coaches or others, the condition of the facility or equipment, or from the normal nature of the training itself. I voluntarily choose to take part and I accept all of these risks, known and unknown.</p>

<h3>3. Release and waiver of claims</h3>
<p>To the fullest extent allowed by law, I release, waive and discharge {RELEASED} from any and all claims, demands, losses and liability for any injury, illness, death, or damage to property that happens to me while taking part in the Activities or while on the premises, <b>including claims caused by the ordinary negligence of the Gym</b>.</p>

<h3>4. Agreement not to sue</h3>
<p>I agree not to sue the Gym, or bring any claim against the Gym, for any injury, death or loss covered by this release. If I or anyone on my behalf brings such a claim, I agree to pay the Gym's reasonable legal fees and costs.</p>

<h3>5. Indemnity</h3>
<p>I agree to defend and hold the Gym harmless from any claims brought by me, my family, my heirs or anyone else that arise from my participation in the Activities.</p>

<h3>6. My health</h3>
<p>I confirm that I am physically able to take part, that I have no medical condition that would make participation unsafe for me or others, and that I will tell a coach about any injury or condition before training. I will stop and tell a coach if I feel unwell or get hurt.</p>

<h3>7. Medical treatment</h3>
<p>If I am injured or unable to respond, I authorize the Gym to call for and get emergency medical care for me. I am responsible for any medical costs.</p>

<h3>8. Rules</h3>
<p>I agree to follow the coaches' instructions and the Gym's rules, including tapping when caught in a submission, respecting training partners' taps, keeping nails short and gear clean, and not training with skin infections.</p>

<h3>9. Minors</h3>
<p>If the participant is under 18, I am their parent or legal guardian. I agree to everything in this waiver on the child's behalf and on my own behalf, and I agree to the release, agreement not to sue and indemnity for any claim brought by or for the child.</p>

<h3>10. General</h3>
<p>This waiver stays in effect for all of my future participation unless I revoke it in writing. It is governed by California law. If any part is found unenforceable, the rest stays in full effect. I have read this waiver, I understand it, and I sign it voluntarily.</p>
'''

WAIVER_CSS = '''<style>
.waiver-text { background: var(--bg-card); border: 1px solid var(--line); border-radius: var(--radius-md); padding: 22px 22px 8px; max-height: 60vh; overflow-y: auto; margin-top: 18px; }
.waiver-text h2 { margin-top: 0; }
.waiver-text h3 { font-family: var(--font-display); font-weight: 800; font-size: 16px; color: var(--fg); margin: 22px 0 8px; text-transform: none; }
.sig { width: 100%; max-width: 100%; height: 180px; background: #fff; border-radius: 10px; border: 1px solid var(--line-strong); touch-action: none; cursor: crosshair; display: block; }
.agree { display: flex; gap: 10px; align-items: flex-start; font-size: 15px; color: var(--fg); }
.agree input { width: 22px; height: 22px; margin-top: 2px; flex: none; accent-color: var(--accent); }
</style>'''

body = f'''<div class="legal-wrap"><div class="wrap">
  <div class="legal" style="max-width:760px">
    {crumbs('Waiver')}
    <p class="kicker" style="margin-top:14px">Required before your first class</p>
    <h1>Liability waiver</h1>
    <p>Every student needs a signed waiver on file before training. It takes about two minutes. Parents or guardians sign for anyone under 18.</p>
    <article class="waiver-text">
{waiver_text}
    </article>

    <form class="form" id="waiverForm" novalidate data-lead="waiver" data-ok="waiverOk" style="margin-top:28px">
      <p class="kicker" style="margin:0">Participant</p>
      <div class="form-row">
        <div class="field"><label for="wName">Participant's full name</label><input id="wName" name="name" type="text" autocomplete="name" required></div>
        <div class="field"><label for="wDob">Date of birth</label><input id="wDob" name="dob" type="date" required></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="wPhone">Phone</label><input id="wPhone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>
        <div class="field"><label for="wEmail">Email</label><input id="wEmail" name="email" type="email" autocomplete="email" inputmode="email" required></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="wEmName">Emergency contact name</label><input id="wEmName" name="emergency_name" type="text" required></div>
        <div class="field"><label for="wEmPhone">Emergency contact phone</label><input id="wEmPhone" name="emergency_phone" type="tel" inputmode="tel" required></div>
      </div>
      <div class="field"><label for="wMed">Injuries or medical conditions a coach should know about</label><input id="wMed" name="medical" type="text" placeholder="Optional"></div>

      <div class="field" id="guardianBox" hidden>
        <p class="kicker" style="margin:6px 0 0">Parent or guardian (participant is under 18)</p>
        <label for="wGuardian">Parent or guardian's full name</label>
        <input id="wGuardian" name="guardian_name" type="text">
      </div>

      <div class="field">
        <label for="wSig">Signature <span style="font-weight:500;text-transform:none;letter-spacing:0">(draw with your finger or mouse)</span></label>
        <canvas id="wSig" class="sig" width="600" height="180" aria-label="Signature pad" role="img"></canvas>
        <div style="display:flex;justify-content:space-between;gap:12px;align-items:center"><span class="form-fine" id="sigWho">Signed by the participant</span><button type="button" class="link" id="sigClear" style="background:none;border:0;cursor:pointer;color:var(--accent)">Clear</button></div>
        <input type="hidden" name="signature" id="wSigData">
      </div>
      <label class="agree"><input type="checkbox" id="wAgree" name="agree" value="yes" required> I have read this waiver, I understand that I am giving up legal rights including the right to sue, and I agree to it.</label>
      <input type="hidden" name="signed_at" id="wSignedAt">
      <button class="btn btn-primary btn-block" type="submit">Sign waiver</button>
      <p class="form-fine">Questions? Call or text {PHONE}.</p>
    </form>
    <div class="form-ok" id="waiverOk" hidden style="margin-top:28px">
      <p class="kicker">Waiver signed</p>
      <p class="display">You're all set</p>
      <p>Thanks, <span data-ok-name>friend</span>. Your waiver is on file. See you on the mat.</p>
    </div>
  </div>
</div></div>
{WAIVER_CSS}
<script>
(function () {{
  var c = document.getElementById('wSig'), x = c.getContext('2d'), drawing = false, has = false;
  function size() {{ var r = c.getBoundingClientRect(), s = window.devicePixelRatio || 1; c.width = r.width * s; c.height = r.height * s; x.scale(s, s); x.lineWidth = 2.4; x.lineCap = 'round'; x.lineJoin = 'round'; x.strokeStyle = '#111113'; has = false; }}
  size(); window.addEventListener('resize', size);
  function pt(e) {{ var r = c.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }}
  c.addEventListener('pointerdown', function (e) {{ drawing = true; c.setPointerCapture(e.pointerId); var p = pt(e); x.beginPath(); x.moveTo(p[0], p[1]); }});
  c.addEventListener('pointermove', function (e) {{ if (!drawing) return; var p = pt(e); x.lineTo(p[0], p[1]); x.stroke(); has = true; }});
  c.addEventListener('pointerup', function () {{ drawing = false; if (has) {{ document.getElementById('wSigData').value = c.toDataURL('image/png'); c.style.borderColor = ''; }} }});
  document.getElementById('sigClear').addEventListener('click', function () {{ x.clearRect(0, 0, c.width, c.height); has = false; document.getElementById('wSigData').value = ''; }});
  // Under 18: ask for the parent or guardian, who signs
  var dob = document.getElementById('wDob'), gBox = document.getElementById('guardianBox'), g = document.getElementById('wGuardian');
  dob.addEventListener('change', function () {{
    var d = new Date(dob.value), t = new Date(), age = t.getFullYear() - d.getFullYear() - ((t.getMonth() < d.getMonth() || (t.getMonth() === d.getMonth() && t.getDate() < d.getDate())) ? 1 : 0);
    var minor = dob.value && age < 18; gBox.hidden = !minor; g.required = !!minor;
    document.getElementById('sigWho').textContent = minor ? 'Signed by the parent or guardian' : 'Signed by the participant';
  }});
  // Signature is required; time-stamp the signing
  document.getElementById('waiverForm').addEventListener('submit', function (e) {{
    document.getElementById('wSignedAt').value = new Date().toISOString();
    if (!has) {{ e.preventDefault(); e.stopImmediatePropagation(); c.style.borderColor = '#f0544f'; c.scrollIntoView({{ behavior: 'smooth', block: 'center' }}); }}
    var a = document.getElementById('wAgree'); if (!a.checked) {{ e.preventDefault(); e.stopImmediatePropagation(); a.focus(); }}
  }}, true);
}})();
</script>'''

w('waiver/index.html', page('Liability Waiver | Costa Mesa Jiu Jitsu',
    'Sign the Costa Mesa Jiu Jitsu liability waiver online before your first class. Parents or guardians sign for students under 18.',
    '/waiver/', body, noindex=True, ld=[ORG, crumbs_ld('Waiver', '/waiver/')]))
print('waiver page built')
