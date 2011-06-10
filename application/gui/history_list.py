import os
import gtk

COL_NAME		= 0
COL_PATH		= 1
COL_TIMESTAMP	= 2


class HistoryList(gtk.Window):
	"""History list is used to display complete browsing history."""

	def __init__(self, parent, application):
		# create main window
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

		# store parameters locally, we'll need them later
		self._parent = parent
		self._application = application

		# configure dialog
		self.set_title(_('History'))
		self.set_size_request(500, 300)
		self.set_resizable(True)
		self.set_skip_taskbar_hint(True)
		self.set_modal(True)
		self.set_transient_for(application)
		self.set_wmclass('Sunflower', 'Sunflower')
		self.set_border_width(7)

		# create UI
		vbox = gtk.VBox(False, 7)

		list_container = gtk.ScrolledWindow()
		list_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		list_container.set_shadow_type(gtk.SHADOW_IN)

		self._history = gtk.ListStore(str, str)

		cell_name = gtk.CellRendererText()
		cell_path = gtk.CellRendererText()

		col_name = gtk.TreeViewColumn(_('Name'), cell_name, text=COL_NAME)
		col_path = gtk.TreeViewColumn(_('Path'), cell_path, text=COL_PATH)

		self._history_list = gtk.TreeView(self._history)
		self._history_list.connect('key-press-event', self._handle_key_press)
		self._history_list.append_column(col_name)
		self._history_list.append_column(col_path)

		# create controls
		hbox_controls = gtk.HBox(False, 5)

		btn_close = gtk.Button(stock=gtk.STOCK_CLOSE)
		btn_close.connect('clicked', self._close)

		image_jump = gtk.Image()
		image_jump.set_from_icon_name('go-jump', gtk.ICON_SIZE_BUTTON)

		btn_jump = gtk.Button()
		btn_jump.set_image(image_jump)
		btn_jump.set_label(_('Go to'))
		btn_jump.set_can_default(True)
		btn_jump.connect('clicked', self._change_path)

		image_new_tab = gtk.Image()
		image_new_tab.set_from_icon_name('tab-new', gtk.ICON_SIZE_BUTTON)

		btn_new_tab = gtk.Button()
		btn_new_tab.set_image(image_new_tab)
		btn_new_tab.set_label(_('New tab'))
		btn_new_tab.set_tooltip_text(_('Open selected path in new tab'))
		btn_new_tab.connect('clicked', self._open_in_new_tab)

		# pack UI
		list_container.add(self._history_list)

		hbox_controls.pack_end(btn_close, False, False, 0)
		hbox_controls.pack_end(btn_jump, False, False, 0)
		hbox_controls.pack_start(btn_new_tab, False, False, 0)

		vbox.pack_start(list_container, True, True, 0)
		vbox.pack_start(hbox_controls, False, False, 0)

		self.add(vbox)

		# populate history list
		self._populate_list()

		# show all elements
		self.show_all()

	def _close(self, widget=None, data=None):
		"""Handle clicking on close button"""
		self.destroy()

	def _change_path(self, widget=None, data=None):
		"""Change to selected path"""
		selection = self._history_list.get_selection()
		list_, iter_ = selection.get_selected()

		# if selection is valid, change to selected path
		if iter_ is not None:
			path = list_.get_value(iter_, COL_PATH)

			# change path
			self._parent._handle_history_click(path=path)

			# close dialog
			self._close()

	def _open_in_new_tab(self, widget=None, data=None):
		"""Open selected item in new tab"""
		selection = self._history_list.get_selection()
		list_, iter_ = selection.get_selected()

		# if selection is valid, change to selected path
		if iter_ is not None:
			path = list_.get_value(iter_, COL_PATH)

			# create new tab
			self._application.create_tab(
							self._parent._notebook,
							self._parent.__class__,
							path
						)

			# close dialog
			self._close()

	def _handle_key_press(self, widget, event, data=None):
		"""Handle pressing keys in history list"""
		result = False
		key_name = gtk.gdk.keyval_name(event.keyval)

		if key_name == 'Return':
			if event.state & gtk.gdk.CONTROL_MASK:
				# open path in new tab
				self._open_in_new_tab()

			else:
				# open path in existing tab
				self._change_path()

			result = True

		elif key_name == 'Escape':
			# close window on escape
			self._close()
			result = True

		return result

	def _populate_list(self):
		"""Populate history list"""
		for path in self._parent.history[1:]:
			name = os.path.basename(path)
			if name == '':
				name = path

			self._history.append((name, path))

		# select first item
		self._history_list.set_cursor((0,))