import subprocess
import argparse
import pathlib
import os
import shutil
import re


def check_bibliography(tex_filename: str | pathlib.Path) -> pathlib.Path | None:
    """
    Parameters
    ----------
    tex_filename: str | pathlib.Path
        Path to the `.tex` file that you want to check the existence of `\\bibliography{...}` for.

    Returns
    -------
    result: pathlib.Path | None
        The path of the bibliography file that is cited in `\\bibliography{...}` if it exists in the `.tex` file, else `None`.
    """
    if isinstance(tex_filename, str):
        tex_filename = pathlib.Path(tex_filename)
    assert tex_filename.is_file()
    # Matches `\bibliography...`. Courtesy of GPT-3.5.
    bibliographyfile = re.findall(
        pattern=r"^\\(bibliography{)([^{}]*)(})",
        string=tex_filename.read_text(),
        flags=re.MULTILINE,
    )
    assert (
        len(bibliographyfile) <= 1
    ), f"{len(bibliographyfile) = }. There should be only at most one match!"
    if len(bibliographyfile) == 1:
        result = pathlib.Path(bibliographyfile[0][1])
    else:
        result = None
    return result


def update_bibliography(
    tex_filename: str | pathlib.Path, new_bibliography_filename: str
) -> None:
    """
    Parameters
    ----------
    tex_filename: str | pathlib.Path
        Path to the `.tex` file that you want to update `\\bibliography{...}` for.

    new_bibliography_filename: str
        Name of the new bibliography file that you want to insert into `\\bibliography{...}`.

    Returns
    -------
    None
    """
    if isinstance(tex_filename, str):
        tex_filename = pathlib.Path(tex_filename)
    assert tex_filename.is_file()
    new_text_string = re.sub(
        # pattern=r"^\s*\\bibliography[^\{]*\{([^{}]*)\}",
        pattern=r"(\s*\\bibliography[^\{]*\{)([^{}]*)(\})([^\n]*)",
        repl=rf"\1{new_bibliography_filename}\3\4",
        string=tex_filename.read_text(),
        flags=re.MULTILINE,
    )
    with open(tex_filename, "w") as texfile:
        texfile.write(new_text_string)


def is_tool(name: str) -> bool:
    """
    Check whether `name` is on PATH and marked as executable. Reference: https://stackoverflow.com/a/34177358/15587966.

    Parameters
    ----------
    name: str
        Name of the tool that you want to check whether is installed and added to PATH.

    Returns
    bool
        `True` if the tool is installed and added to PATH, else `False`.
    """
    return shutil.which(name) is not None


def generate_bbl(tex_filename: str | pathlib.Path) -> None:
    """
    Parameters
    ----------
    tex_filename: str | pathlib.Path
        Path to the `.tex` file that you want to generate `.bbl` file for. Nothing will be generated if `\\bibliography{...}` is not found.

    Returns
    -------
    None
    """
    if isinstance(tex_filename, str):
        tex_filename = pathlib.Path(tex_filename)
    assert tex_filename.is_file()
    bibfile = check_bibliography(tex_filename=tex_filename)
    if not (bibfile is None):
        output_folder = tex_filename.parent
        assert output_folder.is_dir()
        return_code = subprocess.call(
            [
                "pdflatex",
                "-shell-escape",
                "-halt-on-error",
                "-interaction=batchmode",
                f"-output-directory={output_folder.as_posix()}",
                tex_filename.as_posix(),
            ]
        )
        assert return_code == 0
        assert tex_filename.with_suffix(".aux").is_file()
        cwd = os.getcwd()
        os.chdir(output_folder)
        return_code = subprocess.call(
            [
                "bibtex",
                tex_filename.stem,
            ]
        )
        os.chdir(cwd)
        assert return_code == 0


def generate_expanded_tex(
    texfile: str | pathlib.Path,
    expanded_tex_filename: None | str | pathlib.Path = None,
    embed_bbl: bool = False,
    bibfile: str = "bibfile",
    clean_up: bool = True,
):
    """
    Generates an expanded `.tex` file with the presence of a `.bib` file. Uses `latexpand`.

    Parameters
    ----------
    texfile : str or pathlib.Path
        Relative or absolute path to the `.tex` file that you want to expand

    expanded_tex_filename : str or pathlib.Path
        Relative or absolute path to the resulting expanded `.tex` file. By default it is the same as `texfile` appended with '_expanded'.

    embed_bbl : bool
        A boolean flag that if set to `True`, will result in the content of your `.bbl` file to be embedded in the resulting expanded `.tex` file.
        Note that the `.bbl` file is automatically generated from your `.bib` file. By default, this flag is set to `False`.

    bibfile: str
        Name of your `.bib` file without the file extension. By default, it is set to 'bibfile'.

    clean_up: bool
        If `True`, a clean up via `latexmk -C` will be performed after generating the expanded `.tex` file, else do nothing. By default, this is set to `True`.

    Returns
    -------
    expanded_tex_filename: pathlib.Path
        Path to the resulting expanded `.tex` file.
    """
    if isinstance(texfile, str):
        texfile = pathlib.Path(texfile)
    assert texfile.is_file()
    if expanded_tex_filename == None:
        expanded_tex_filename = pathlib.Path(texfile.stem + "Expanded.tex")
    if isinstance(expanded_tex_filename, str):
        expanded_tex_filename = pathlib.Path(expanded_tex_filename)

    bibfile = check_bibliography(tex_filename=texfile)
    if not (bibfile is None):
        bibfile = bibfile.name
        biber_args = (
            "--biber",
            f"{bibfile}",
        )
        assert (texfile.parent / f"{bibfile}.bib").is_file()
        bblfile = texfile.with_suffix(".bbl")
        assert bblfile.is_file()
    else:
        biber_args = ()
    if embed_bbl and not (bibfile is None):
        embed_bbl_args = (
            "--expand-bbl",
            bblfile.as_posix(),
        )
    else:
        embed_bbl_args = ()
    cwd = os.getcwd()
    os.chdir(texfile.parent)
    return_code = subprocess.call(
        [
            "latexpand",
            "--empty-comments",
            *biber_args,
            *embed_bbl_args,
            texfile.as_posix(),
            "--output",
            expanded_tex_filename.as_posix(),
        ],
    )
    assert expanded_tex_filename.is_file()
    assert return_code == 0
    if not embed_bbl and not (bibfile is None):
        check_bibliography(tex_filename=expanded_tex_filename)
        generate_bbl(expanded_tex_filename)
        update_bibliography(
            tex_filename=expanded_tex_filename,
            new_bibliography_filename=f"{expanded_tex_filename.stem}.bbl",
        )
    if clean_up:
        return_code = subprocess.call(["latexmk", "-C"])
        assert return_code == 0
    os.chdir(cwd)
    return expanded_tex_filename


def main(
    temporary_working_directory: None | str = None,
    input_tex: None | str = None,
    embed_bbl: None | bool = None,
) -> None:
    # Check for the executable required.
    executables_required = ("latexpand", "bibtex")
    for executable_required in executables_required:
        assert is_tool(
            executable_required
        ), f"\x1b[0;91mPlease install '{executable_required}' or make sure it is in path. TeXLive is recommended.\x1b[0m"

    # Set up the command line argument parser.
    if (
        (temporary_working_directory is None)
        and (input_tex is None)
        and (embed_bbl is None)
    ):
        parser = argparse.ArgumentParser(
            prog="pylatexpand",
            description="\x1b[1;3;4;92mPython wrapper for latexpand and bibtex\x1b[0m",
            epilog="Written by Wo",
        )
        parser.add_argument(
            "-i",
            "--input-main-tex-file",
            type=str,
            required=True,
            help="name of the input tex file. File extension is optional",
        )
        parser.add_argument(
            "-C",
            "--temporary-working-directory",
            type=str,
            required=False,
            help="temporarily change to your desired working directory",
        )
        parser.add_argument(
            "-E",
            "--expanded-tex-filename",
            type=str,
            required=False,
            help="expanded tex filename",
        )
        parser.add_argument(
            "--embed-bbl",
            action=argparse.BooleanOptionalAction,
            default=False,
            required=False,
            help="whether to embed `.bbl` file within the expanded `.tex` file or not (default=False). Note that the generation of `.bbl` is always automated. This option is ignored if no `\\bibliography{...}` is found within the input main `.tex` file.",
        )

        args = parser.parse_args()
        input_main_tex_file = pathlib.Path(args.input_main_tex_file)
        expanded_tex_filename = args.expanded_tex_filename
        temporary_working_directory = args.temporary_working_directory
        embed_bbl = args.embed_bbl
    else:
        input_main_tex_file = pathlib.Path(input_tex)
        expanded_tex_filename = None

    # Handle the command line arguments supplied by the user
    if expanded_tex_filename is not None:
        expanded_tex_filename = pathlib.Path(args.expanded_tex_filename)
        if expanded_tex_filename.stem == expanded_tex_filename.as_posix():
            expanded_tex_filename = expanded_tex_filename.with_suffix(".tex")
        if expanded_tex_filename.suffix != ".tex":
            parser.error(f"Expanded tex file's extension must be .tex!")

    # If the input argument doesn't contain a file extension, automatically add .tex to it
    if input_main_tex_file.stem == input_main_tex_file.as_posix():
        input_main_tex_file = input_main_tex_file.with_suffix(".tex")
    if input_main_tex_file.suffix != ".tex":
        parser.error(f"Input file's extension must be .tex!")
    if temporary_working_directory is not None:
        temporary_working_directory = pathlib.Path(temporary_working_directory)
        assert (
            temporary_working_directory.is_dir()
        ), f"{temporary_working_directory} is not a directory"
        cwd = os.getcwd()
        os.chdir(temporary_working_directory)
    if not input_main_tex_file.is_file():
        parser.error(f"Input {input_main_tex_file} file not found!")

    # Generate the `.bbl` file where appropriate.
    generate_bbl(input_main_tex_file)

    # Generate the expanded `.tex` file.
    expanded_tex_filename = generate_expanded_tex(
        input_main_tex_file,
        expanded_tex_filename=expanded_tex_filename,
        embed_bbl=embed_bbl,
    )
    # LaTeX processing done.
    print("\x1b[0;92mDone\x1b[0m")

    # Information printing.
    if temporary_working_directory is not None:
        os.chdir(cwd)
        resulting_str = temporary_working_directory / expanded_tex_filename
    else:
        resulting_str = expanded_tex_filename
    print(
        f"Expanded .tex file located at \x1b[1;4;93m{resulting_str.as_posix()}\x1b[0m"
    )
    print(
        f"You can build the .pdf via the command \x1b[1;4;96mlatexmk -bibtex- -silent -pdf {resulting_str.name}\x1b[0m. For help, see \x1b[1;4;96mlatexmk --help\x1b[0m."
    )
    if not is_tool("latexmk"):
        print(
            "Note that you would have to install \x1b[1;4;96mlatexmk\x1b[0m or add it to PATH. TexLive is recommended."
        )


if __name__ == "__main__":
    main()
