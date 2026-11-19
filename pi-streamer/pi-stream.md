

## Hardware
**SMSL SU-1**
https://www.maxgaming.no/no/eksternt-lydkort/smsl-su-1-stereo-dac

## Software
Volumio or Moode

Headless setup — both are designed for it: 

Volumio (easiest first boot):

Flash the image, plug in Ethernet (or nothing), power on
If no Ethernet, it creates a hotspot: SSID Volumio, password volumio2
Connect to it, open http://volumio.local (or 192.168.211.1)
A setup wizard walks you through naming the device, choosing your Wi-Fi, and selecting your DAC
Done — control it from any browser or the mobile app on your LAN 

Moode (requires one extra step before first boot):

Use Raspberry Pi Imager to flash the card — it's in the "Media Player OS" section. You must set a username/password and enable SSH in Imager's settings before writing, or it won't function. 
Optionally enter your Wi-Fi SSID/password in Imager too (saves the hotspot step)
Power on — expect 3 automatic reboots on first boot (be patient)
Connect via your LAN: http://moode.local (or the IP). If you didn't pre-set Wi-Fi, it opens an AP: SSID moode, password moodeaudio, IP 172.24.1.1
Configure from the browser — output device, volume, etc. 
One Pi 3B+ caveat for Moode: the 1 GB RAM is enough for Spotify Connect, but the librespot build is slow (~45 min) and can fail if memory gets tight. If you're not using Spotify Connect, it's a non-issue. 

Either way, once the SMSL SU-1 arrives you just go to the output settings in the web UI and switch from the onboard jack to the USB DAC.

## Log: Spotify Connect on Moode (Pi 3B+, 2026-11-18)

**Spotify Connect install**
- First attempt through the Moode UI stalled. Root cause: the Moode installer compiles librespot from source, and the first attempt was interrupted by a dropped connection.
- Test install of Raspotify (`curl -sL https://dtcooper.github.io/raspotify/install.sh | sh`) worked as a package, but it failed at playback: the ALSA `default` device was busy or invalid, and the service exited.
- Raspotify was disabled and removed (`sudo systemctl disable --now raspotify`, `sudo apt remove -y raspotify`). It's now in `rc` state (config files left behind, harmless). Optional cleanup: `sudo apt purge -y raspotify`.
- Second Moode UI install was run from a `tmux` session (`spotify2`) on Ethernet. Build ran about 19:08 to 20:04. Install step succeeded and the log ended with "Update installed, restart required".
- Swap is 4 GB (`swapon --show`). Memory was not the limiting factor on the second attempt.
- Next steps: restart the Pi, check Spotify Connect is enabled in the Moode UI, then test from the Spotify app.

**Audio output**
- Moode's web UI only lists HDMI output (`vc4hdmi`). `/proc/asound/cards` and `aplay -l` show no headphone card.
- Cause: the kernel command line in `/boot/firmware/cmdline.txt` includes `snd_bcm2835.enable_headphones=0`, which disables the onboard jack. `dtparam=audio=on` is already set in `config.txt`, so that's not the problem.
- Plan: use the SMSL SU-1 over USB when it arrives. No boot changes are needed for that.

**Enabling the headphone jack (attempted, not working)**
- Tried editing `/boot/firmware/cmdline.txt`. That was wrong: the file doesn't contain `snd_bcm2835.enable_headphones`, so the `sed` changed nothing.
- The running kernel gets `snd_bcm2835.enable_headphones=0` (and `enable_hdmi=0`) from the device tree bootargs (`/proc/device-tree/chosen/bootargs`), not from `cmdline.txt` or `config.txt`.
- Changing it means editing the `.dtb` on `/boot/firmware` (e.g. `bcm2710-rpi-3-b-plus.dtb`) or a Moode-specific boot file, which hasn't been done. Not recommended without a backup.
- Status: the onboard jack is disabled on this image. Plan is to use the SMSL SU-1 over USB. Spotify Connect works (confirmed from the Spotify app).

**Once the DAC arrives**
- Plug in the SU-1, check `aplay -l` for a USB card, and select it in Moode's Audio settings.
- Test playback from the Spotify app.
- If Moode's support forum confirms how to enable the jack on this image, add those steps here.

## Plan: Raspberry Pi OS Lite on a second SD card (headphone jack test + Raspotify)

Goal: get Spotify Connect playing through the Pi's headphone jack while waiting for the SU-1. Moode's image disables the jack, so this uses a separate card with Raspberry Pi OS Lite, which leaves the jack enabled by default.

**1. Flash the image**
1. Insert the second SD card into the PC (use a card reader). Check the drive letter first so you don't overwrite the Moode card.
2. Open Raspberry Pi Imager and choose:
   - Device: Raspberry Pi 3
   - OS: Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit) (Bookworm or later)
   - Storage: the second SD card only
3. Click Next, then Edit Settings (OS customisation):
   - Hostname: `pi-lite` (so it doesn't clash with `moode.local`)
   - Username and password: set your own
   - Enable SSH (password authentication is fine for now)
   - Configure wireless LAN: your SSID and password, country `NO`
   - Set the locale and timezone
4. Write the image and wait for verification to finish.

**2. First boot**
1. Put the card in the Pi, power on, and wait about 1–2 minutes.
2. From the PC: `ssh <username>@pi-lite.local` (or find the IP in your router). Accept the host key.
3. Update the system:
   ```
   sudo apt update && sudo apt full-upgrade -y
   sudo reboot
   ```
4. SSH back in after the reboot.

**3. Check the headphone jack (stop here if this fails)**
1. Confirm the onboard audio card exists:
   ```
   cat /proc/asound/cards
   aplay -l
   ```
   Expected: a card named `bcm2835 Headphones` (card 0). If you only see `vc4hdmi`, the jack is disabled.
2. Check that the boot files don't disable it. Both of these should show no `enable_headphones=0`:
   ```
   grep -o 'snd_bcm2835[^ ]*' /boot/firmware/cmdline.txt
   grep -i audio /boot/firmware/config.txt
   ```
   `dtparam=audio=on` should be present (uncommented). If it isn't, add `dtparam=audio=on` to `/boot/firmware/config.txt` and reboot.
3. Route audio to the jack and set volume:
   ```
   amixer cset numid=3 1
   amixer -c 0 set PCM 80%
   ```
   (`numid=3` value `1` = analog/headphones, `2` = HDMI, `0` = auto.)
4. Test the jack:
   ```
   speaker-test -c2 -t wav -l 1
   ```
   Press Ctrl+C to stop. You should hear the voice in your headphones (left/right alternating).
5. **Decision:** if a `Headphones` card shows up and the test sounds through the jack, continue to step 4. If not, don't install Raspotify yet. Check the wiring/hardware first, or fall back to waiting for the SU-1.

**4. Install Raspotify (only after step 3 passes)**
1. Install it:
   ```
   curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
   ```
2. Point it at the jack. Edit `/etc/raspotify/conf` and set the device to the headphone card, e.g. `LIBRESPOT_DEVICE="hw:0,0"` (check the commented examples in that file for the exact variable names in your Raspotify version). Optionally set `LIBRESPOT_NAME="Pi Lite"` so it's easy to spot in the Spotify app.
3. Restart and check:
   ```
   sudo systemctl restart raspotify
   sudo systemctl status raspotify
   journalctl -u raspotify -n 50
   ```
   The service should be `active (running)` with no ALSA "device busy" or "invalid" errors (those were the failure on the Moode attempt).
4. In the Spotify app, open the device list and select the new device name. Play something and confirm sound comes out of the jack.

**Notes**
- Keep the Moode card untouched; it's a separate card, so swapping back is just reseating the original card.
- Once the SU-1 arrives, Raspotify on this card can switch to the USB device by changing `LIBRESPOT_DEVICE` (check `aplay -l` for the USB card number).

**Volume**
- The headphone card has no `Master` control. The only volume control is `PCM`, so use `amixer -c 0 set PCM 100%` (check with `amixer -c 0 scontrols`).
- Keep the Pi's `PCM` at 100% and the Spotify slider at or near max. Use the amp's volume for loudness. If anything distorts at high amp settings, lower Spotify.
- Save the ALSA state so the settings survive a reboot: `sudo alsactl store`.

**Result**
- Raspberry Pi OS Lite (64-bit) on the second card, hostname `pi-lite`. Jack confirmed as card 0 (`bcm2835 Headphones`) with `speaker-test` heard through the jack.
- Raspotify working on `hw:0,0`, device name set in `/etc/raspotify/conf`, playback confirmed from the Spotify app.
- Playback, pause, skip and the volume slider tested. Raspotify starts on boot.
