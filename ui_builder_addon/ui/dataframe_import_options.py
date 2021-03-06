import re

import enaml
import traits_enaml
from enaml.qt.qt_application import QtApplication
from traits.api import (
    HasTraits, Str, HTML, List, Int, Bool, Dict, Any, Instance
)
import pandas as pd
from enaml_ui_builder import application
from enaml_ui_builder.app.data_frame_plugin import DataFramePlugin

class DataFrameImportOptions(HasTraits):
    """Class to handle options for importing CSV and model for enaml view.
    """

    # Index of header row
    header_row = Any(0)

    # Indexes of columns to use as index columns
    index_column = Str('None')

    # Indexes entered as comma separated list
    index_sequence = Str()

    # Html to be used in preview of dataframe
    html = HTML()

    # Whether to parse dates
    parse_dates = Bool(False)

    # Path to CSV file
    path = Str()

    # DataFrame for CSV file
    df = pd.DataFrame()

    # CSS for dataframe html
    style = Str("<style type='text/css'>html, body{margin: 0;padding:\
                0;width:100%;}table{width:100%;height:100%;\
                border-collapse:collapse;font-family: monospace;margin:\
                0;border-collapse:collapse;\
                }td{padding: 0 10px;background: #ffffff;}th{text-align:\
                center;padding: 5px;background: #f7f7f7;}</style>")

    application = Instance('envisage.api.IApplication')

    ## Detect Changes in Traits

    def _path_changed(self):
        self._update_dataframe()

    def _header_row_changed(self):
        self._update_dataframe()

    def _index_column_changed(self):
        self._update_dataframe()

    def _index_sequence_changed(self):
        self._update_dataframe()
        
    def _parse_dates_changed(self):
        self._update_dataframe()

    ## Logic for Dataframes and preview

    def _update_dataframe(self):
        # try:
        #     self.df = pd.read_csv(self.path, 
        #                          header=self.header_row,
        #                          parse_dates=self.parse_dates,
        #                          index_col=self._get_current_index_col(),
        #                          encoding='utf-8')
        #     self._update_html()
        # except:
        #     self._update_html_parse_error()
        raise NotImplementedError()

    def _update_html(self):
        self.html = (self.style + self.df.to_html(max_rows=5)).encode('ascii', 'xmlcharrefreplace')

    def _update_html_parse_error(self, error=""):
        error = "<style type='text/css'>*{background:#ffffff;color:red;\
                font-family:monospace;}p{width: 250px; margin: 0 auto;\
                text-align: center;}\
                </style><p>Data could not be parsed.</p><p>"+error+"</p>"
        self.html = error

    def _get_current_index_col(self):
        """Returns index_column converted from string into appropriate datatype
        """
        if self.index_column == 'Multi-Index':
            sequence_array = filter(None, re.compile(r'\d*').findall(self.index_sequence))
            if(len(sequence_array) == 0):
                return None
            else:
                return map(int, sequence_array)
        elif self.index_column == 'None':
            return None
        else:
            return int(self.index_column)

    ## Method called when OK is pressed
    def ok_pressed(self):

        code = """
        import pandas as pd
        df =  pd.read_json('""" + self.df.to_json() + """')
        def _view(dataframe):
            import traits_enaml
            with traits_enaml.imports():
                from misc_views import DialogPopup
            print 'Launching Enaml UI Builder...'
            app = application()
            app.add_plugin(DataFramePlugin(data_frame=dataframe))
            app.start()

        """
        code_task = self.application.get_task('canopy.integrated_code_editor')

        # Make the python pane visible, if it is not
        if not code_task.python_pane.visible:
            code_task.python_pane.visible = True

        # Run the code in the frontend
        code_task.python_pane.frontend.execute_command(code)

        ## Launch UI Builder

        with traits_enaml.imports():
            from misc_views import DialogPopup

        dialog = DialogPopup()

        dialog.show()

        app = application()
        app.add_plugin(DataFramePlugin(data_frame=self.df))
        app.start()

        dialog.close()

        
