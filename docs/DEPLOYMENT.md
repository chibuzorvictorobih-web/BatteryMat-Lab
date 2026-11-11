# Deployment Walkthrough: GitHub and Streamlit

## A. Upload the repository to GitHub

1. Download and **extract** the project ZIP. The extracted folder is named `BatteryMat-Lab`.
2. Sign in to [github.com](https://github.com/).
3. Choose **New repository**, name it `BatteryMat-Lab`, select **Public**, and create it. Do not add a separate README or license at this stage, because the project already includes both.
4. Open the empty repository and select **uploading an existing file** (or **Add file → Upload files**, depending on the GitHub interface).
5. Drag and drop the **contents of the extracted `BatteryMat-Lab` folder** into GitHub's upload area. Preserve subfolders, especially `batterymat/`, `data/`, `.streamlit/`, `docs/`, and `tests/`.
6. Verify that `app.py` and `requirements.txt` appear in the repository root, and that `data/materials.csv` and `batterymat/model.py` are visible in the correct folders. Commit your upload.

**Important:** GitHub does not unpack a ZIP as an application for you. Do not simply upload the ZIP and expect Streamlit to run it. A desktop browser is usually easiest for transferring a multi-folder project. Hidden folders such as `.streamlit/` can be omitted by some file pickers: verify them explicitly after uploading.

### Alternative: Git from a computer

From inside the extracted project folder:

```bash
git init
git add .
git commit -m "Initial BatteryMat-Lab release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/BatteryMat-Lab.git
git push -u origin main
```

Create the empty GitHub repository first and substitute your real GitHub username in the remote URL.

## B. Deploy on Streamlit

1. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Select **Create app** and choose your `BatteryMat-Lab` repository.
3. Set the branch to `main` and **Main file path** to `app.py`.
4. Where the platform offers Python configuration, select Python 3.12 (or another supported version compatible with `requirements.txt`).
5. Click **Deploy**. The platform installs the packages declared in the repository's `requirements.txt` and starts `app.py`.
6. Open the resulting app and verify that the five tabs, charts, calculations, and CSV download buttons work.

A Streamlit Community Cloud app typically has a URL ending in `streamlit.app`. The exact domain is assigned by the platform or selected in its app creation screen.

## C. First deployment checks

- **Cell calculator**: select the default LFP/graphite case and click **Calculate Performance**. The results should read 3.35 V, 1.550 Ah, 5.1925 Wh and approximately 190.2 Wh/kg. Confirm that the Wh/kg unit is fully visible.
- **Invalid inputs**: adjust the electrode potentials so the positive potential is not above the negative potential, then click **Calculate Performance**. A clear warning should appear instead of a blank app. Restore the defaults and calculate again.
- **Chemistry comparison**: eight rows appear (four positive materials × two negative materials).
- **Sensitivity lab**: changing the N/P ratio changes electrode mass and specific energy, but not nominal energy at fixed positive capacity and voltage.
- **Material library**: six source-backed material records are displayed.
- **Method & sources**: assumptions and reference links are visible.

## D. Troubleshooting

- **`ModuleNotFoundError: batterymat`**: the `batterymat/` folder was not uploaded to the repository root.
- **`FileNotFoundError: ... materials.csv`**: confirm `data/materials.csv` is present at the repository root. Do not rename it.
- **Dependency error**: confirm `requirements.txt` is at the root and does not contain any accidentally pasted formatting. Check the Streamlit deployment logs.
- **Blank app or a crash**: review Streamlit's application logs for a Python traceback. Verify the branch and main file path.
- **Missing theme**: check that `.streamlit/config.toml` is present in GitHub; `.streamlit` starts with a dot and may be hidden in a file picker.

## E. Run locally or validate calculations

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run app.py
```

The tests can also run independently of the Streamlit interface using only the Python standard library plus pytest.
