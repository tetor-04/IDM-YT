    def show_context_menu(self, event):
        """Show context menu for tree item"""
        item = self.video_tree.identify_row(event.y)
        if not item:
            return
        
        # Select the item
        self.video_tree.selection_set(item)
        
        # Create context menu with submenus
        context_menu = tk.Menu(self.window, tearoff=0)
        
        # Quality submenu
        quality_menu = tk.Menu(context_menu, tearoff=0)
        quality_menu.add_command(label="Set Quality Dialog...", 
                                command=lambda: self.show_quality_dialog(item))
        quality_menu.add_command(label="Analyze Available Qualities", 
                                command=lambda: self.analyze_item_quality(item))
        quality_menu.add_separator()
        quality_menu.add_command(label="Best Available", 
                                command=lambda: self.set_item_quality(item, "Best Available"))
        quality_menu.add_command(label="1080p", 
                                command=lambda: self.set_item_quality(item, "1080p"))
        quality_menu.add_command(label="720p", 
                                command=lambda: self.set_item_quality(item, "720p"))
        quality_menu.add_command(label="480p", 
                                command=lambda: self.set_item_quality(item, "480p"))
        quality_menu.add_separator()
        quality_menu.add_command(label="Audio Only (Best)", 
                                command=lambda: self.set_item_audio_only(item, "Best Audio"))
        quality_menu.add_command(label="Audio Only (128k)", 
                                command=lambda: self.set_item_audio_only(item, "128k"))
        context_menu.add_cascade(label="Quality", menu=quality_menu)
        
        # Info submenu
        info_menu = tk.Menu(context_menu, tearoff=0)
        info_menu.add_command(label="Show Video Info", 
                             command=lambda: self.show_item_info(item))
        info_menu.add_command(label="Show Thumbnail", 
                             command=lambda: self.show_item_thumbnail(item))
        info_menu.add_command(label="Show Description", 
                             command=lambda: self.show_item_description(item))
        info_menu.add_command(label="Show Stats", 
                             command=lambda: self.show_item_stats(item))
        context_menu.add_cascade(label="Information", menu=info_menu)
        
        # Copy submenu
        copy_menu = tk.Menu(context_menu, tearoff=0)
        copy_menu.add_command(label="Copy URL", 
                             command=lambda: self.copy_item_url(item))
        copy_menu.add_command(label="Copy Title", 
                             command=lambda: self.copy_item_title(item))
        copy_menu.add_command(label="Copy Video ID", 
                             command=lambda: self.copy_item_video_id(item))
        copy_menu.add_command(label="Copy Channel Name", 
                             command=lambda: self.copy_item_channel_name(item))
        copy_menu.add_command(label="Copy Channel URL", 
                             command=lambda: self.copy_item_channel_url(item))
        copy_menu.add_command(label="Copy Thumbnail URL", 
                             command=lambda: self.copy_item_thumbnail_url(item))
        copy_menu.add_separator()
        copy_menu.add_command(label="Copy All Info", 
                             command=lambda: self.copy_item_all_info(item))
        context_menu.add_cascade(label="Copy", menu=copy_menu)
        
        # Open submenu
        open_menu = tk.Menu(context_menu, tearoff=0)
        open_menu.add_command(label="Open Video in Browser", 
                             command=lambda: self.open_item_in_browser(item))
        open_menu.add_command(label="Open Channel", 
                             command=lambda: self.open_item_channel(item))
        open_menu.add_command(label="Open Thumbnail", 
                             command=lambda: self.open_item_thumbnail_browser(item))
        context_menu.add_cascade(label="Open", menu=open_menu)
        
        # Selection submenu
        selection_menu = tk.Menu(context_menu, tearoff=0)
        selection_menu.add_command(label="Select All Above", 
                                  command=lambda: self.select_all_above(item))
        selection_menu.add_command(label="Select All Below", 
                                  command=lambda: self.select_all_below(item))
        selection_menu.add_separator()
        selection_menu.add_command(label="Select Same Uploader", 
                                  command=lambda: self.select_same_uploader(item))
        selection_menu.add_command(label="Select Similar Duration", 
                                  command=lambda: self.select_similar_duration(item))
        context_menu.add_cascade(label="Selection", menu=selection_menu)
        
        context_menu.add_separator()
        context_menu.add_command(label="Download This Item", 
                                command=lambda: self.download_single_item(item))
        context_menu.add_command(label="Skip This Item", 
                                command=lambda: self.skip_item(item))
        context_menu.add_separator()
        context_menu.add_command(label="Remove from List", 
                                command=lambda: self.remove_item_from_list(item))
        
        # Show menu at cursor
        context_menu.tk_popup(event.x_root, event.y_root)
