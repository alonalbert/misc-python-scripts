#!/usr/bin/python3

import tkinter as tk


class QRDisplayDialog(tk.Tk):
  """QR display UI for key provisioning."""

  def __init__(self, parent):
    """Initialize class."""
    tk.Tk.__init__(self, parent)
    self.parent = parent

  def initialize(self, otp_request, remote_auth):
    """Initialize the QR Display UI.

    Create the instruction labels, get QR image, and prepare the UI for display.

    Args:
      otp_request:
      remote_auth: Instance of RemoteAuth 
    """

    # Save parameters -- we'll need to access them from other functions
    self.otp_request = otp_request
    self.remote_auth = remote_auth

    # Instructions
    instructions = (
        'Scan this QR code with your phone\'s barcode scanner application to '
        'authorize this account for remote OTP fetching')
    instruction_message = tk.Message(
        self, width=400, text=instructions, font=('Helvetica', 11))
    instruction_message.pack(pady=10)

    # Build data object for QR Code
    data_obj = {'devaddr': lightblue.gethostaddr(),
                'devname': lightblue.finddevicename(lightblue.gethostaddr()),
                'key': self.otp_request.key_info.key}
    data_url = 'bpvauth://remoteaccess?' + urllib.urlencode(data_obj)

    if remote_auth.options.verbose:
      print '-'*80
      print '  Need to associate account with phone'
      print '    Generated QR Code.'
      print '    Data:', data_url

    # Get QR image from google chart server
    chart = pygooglechart.QRChart(320, 320)
    chart.add_data(data_url)
    chart.set_ec('H', 0)
    image_path = '/tmp/.qr%s.png' % time.time()
    chart.download(image_path)
    os.chmod(image_path, stat.S_IRUSR)

    # Set QR image
    global img
    img = ImageTk.PhotoImage(Image.open(image_path))
    os.remove(image_path)
    label_image = tk.Label(self, image=img)
    label_image.pack(pady=10)

    # "OK, I scanned it" Button
    ok_button = tk.Button(self, text='OK, I scanned it', command=self.OK)
    ok_button.pack(pady=10)

    # "Cancel"
    ok_button = tk.Button(self, text='Cancel', command=self.Exit)
    ok_button.pack(pady=5)

    # Set up the geometry related options
    self.resizable(False, False)
    CenterWindow(self, 430, 510)
    self.update()

  def OK(self):
    """Save key data to config and kill UI."""
    self.remote_auth.UpdateConfig(
        None, self.otp_request.device.address, self.otp_request.key_info)
    self.destroy()

  def Exit(self):
    """Kill the whole application."""
    sys.exit(remote_auth_lib.Errors.USER_CANCEL_QR_KEY_PROVISION_LOOP)


if __name__ == '__main__':
    main()
