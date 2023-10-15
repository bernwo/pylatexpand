from bin import main
import subprocess
import os
import pathlib


def test_assignment_no_embed_bbl():
    """
    This tests the building the the expanded `.tex` file from the `tex_project_assignment` folder. This tex project does not contain any `.bib` file. `pylatexpand` should be able to detect this automatically and handle accordingly. The options `--embed-bbl` and `--no-embed-bbl` will be ignored.
    """
    cwd = os.getcwd()
    temporary_working_directory = "tests/tex_project_assignment"
    assert pathlib.Path(temporary_working_directory).is_dir()
    os.chdir(temporary_working_directory)
    return_code = subprocess.call(("latexmk", "-silent", "-C"))
    assert return_code == 0
    for filename in pathlib.Path("./").glob("*.bbl"):
        filename.unlink(missing_ok=True)
    pathlib.Path("mainExpanded.tex").unlink(missing_ok=True)
    os.chdir(cwd)
    main(
        temporary_working_directory=temporary_working_directory,
        input_tex="main.tex",
        embed_bbl=False,
    )
    assert (pathlib.Path(temporary_working_directory) / "mainExpanded.tex").is_file()
    assert not (
        pathlib.Path(temporary_working_directory) / "mainExpanded.bbl"
    ).is_file()


def test_assignment_embed_bbl():
    """
    This tests the building the the expanded `.tex` file from the `tex_project_assignment` folder. This tex project does not contain any `.bib` file. `pylatexpand` should be able to detect this automatically and handle accordingly. The options `--embed-bbl` and `--no-embed-bbl` will be ignored.
    """
    cwd = os.getcwd()
    temporary_working_directory = "tests/tex_project_assignment"
    assert pathlib.Path(temporary_working_directory).is_dir()
    os.chdir(temporary_working_directory)
    return_code = subprocess.call(("latexmk", "-silent", "-C"))
    assert return_code == 0
    for filename in pathlib.Path("./").glob("*.bbl"):
        filename.unlink(missing_ok=True)
    pathlib.Path("mainExpanded.tex").unlink(missing_ok=True)
    os.chdir(cwd)
    main(
        temporary_working_directory=temporary_working_directory,
        input_tex="main.tex",
        embed_bbl=True,
    )
    assert (pathlib.Path(temporary_working_directory) / "mainExpanded.tex").is_file()
    assert not (
        pathlib.Path(temporary_working_directory) / "mainExpanded.bbl"
    ).is_file()
