# TPSRM Automation Sync (Auditboard/Upgaurd)

- Install python
- From the project root folder, run -  
    ```
    pip install -r requirements.txt
    ```
- Run the main.py script and choose options accordingly
    ```
    python main.py
    ```
- Please use `pip3` or `python3` in those commands if you are using python3.

## Notes
- For finding vendors without supplier ID (option 1) - output file is in the `data` folder with path `./data/auditboardDataNoSupplierId.json`
- Once updates are made on either Upgaurd/Auditboard and you wish to make another update, exit and rerun the `python main.py` command. This pulls the updated data once again
- There is a chance that the API call to Upgaurd may fail - this is because of their API throttling. The error looks something like below - this happens when you try to run the script repeatedly, rerun the script after 10-15 minutes if you encounter this. 
    ```
    aiohttp.client_exceptions.ContentTypeError: 0, message='Attempt to decode JSON with unexpected mimetype: text/html; charset=utf-8', url=URL('https://cyber-risk.upguard.com/api/public/vendors?labels=Workday+Active&page_token=5000')
    ```
- For the mapping of fields, there is a configuration file for auditboard/upgaurd labels for TPSRM fields (custom_text_14, custom_field_tpsp_status_id,..etc.). The file can be found in the project root - `./mapping.py`
- If any field name label changes on audtiboard - make the update in `mapping.py` under the `"field mapping[auditboard]"` against that specific field key


