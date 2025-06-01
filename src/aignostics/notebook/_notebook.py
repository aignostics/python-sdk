# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "aignostics",
# ]
# ///

import marimo

__generated_with = "0.13.15"
app = marimo.App(width="full")


@app.cell
def _():
    """Aignostics Notebook

    Notes:
    - See https://colab.research.google.com/github/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/pathomics/microscopy_dicom_ann_intro.ipynb#scrollTo=fMRsnFlzinO5

    """
    import os
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    from cloudpathlib import GSPath
    from dotenv import load_dotenv
    from aignostics import dataset
    from wsidicom import WsiDicom

    mo.sidebar([
        mo.md("# aignostics"),
        mo.nav_menu(
            {
                "#/home": f"{mo.icon('lucide:home')} Home",
                "#/about": f"{mo.icon('lucide:user')} Help",
                "Links": {
                    "https://platform.aignostics.com": "Platform",
                    "https://github.com/aignotics/python-sdk": "GitHub",
                },
            },
            orientation="vertical",
        ),
    ])
    return Path, WsiDicom, dataset, mo, plt


@app.cell
def _(Path, mo):
    query_params = mo.query_params()
    application_run_id = query_params["application_run_id"]
    print(f"Application run id '{application_run_id}'")
    mo.vstack([
        mo.ui.file_browser(
            Path(query_params["results_folder"]),
            filetypes=[".dcm", ".tif", ".tiff", ".svs"],
            multiple=True,
            restrict_navigation=True,
        )
    ])
    return


@app.cell
def _(dataset):
    idc_client = dataset.IDCClient()  # set-up idc_client
    idc_client.fetch_index("sm_instance_index")
    return (idc_client,)


@app.cell
def _(idc_client):
    query_sr = """
    SELECT
        SeriesInstanceUID,
        StudyInstanceUID,
        PatientID,
        collection_id
    FROM
        index
    WHERE
        analysis_result_id = 'Pan-Cancer-Nuclei-Seg-DICOM' AND Modality = 'ANN' AND collection_id = 'tcga_luad'
    ORDER BY
        crdc_series_uuid
    LIMIT 1
    """
    pan_ann = idc_client.sql_query(query_sr)
    return (pan_ann,)


@app.cell
def _(idc_client, pan_ann):
    study_instance_id = pan_ann["StudyInstanceUID"].iloc[0]
    viewer_url = idc_client.get_viewer_URL(
        studyInstanceUID=study_instance_id, viewer_selector="slim"
    )
    from IPython.display import IFrame

    IFrame(viewer_url, width=1260, height=900)
    return


@app.cell
def _(Path, WsiDicom, idc_client, plt):
    series_instance_uid = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"  # copied from slimviewer info box
    idc_client.download_from_selection(
        seriesInstanceUID=series_instance_uid,
        downloadDir="tmp/",
        dirTemplate="%SeriesInstanceUID",
        use_s5cmd_sync=True,
    )
    print(Path(f"tmp/{series_instance_uid}").exists())
    slide = WsiDicom.open(f"tmp/{series_instance_uid}")

    fig, axes = plt.subplots(1, 1, figsize=(12, 6))
    thumbnail = slide.read_thumbnail()
    print(axes)
    axes.imshow(thumbnail)
    axes.axis("off")
    plt.show()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
