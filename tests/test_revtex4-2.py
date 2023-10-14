from bin import main


def test_revtex_no_embed_bbl():
    main(
        temporary_working_directory="tests/tex_project_revtex4-2",
        input_tex="main.tex",
        embed_bbl=False,
    )


def test_revtex_embed_bbl():
    main(
        temporary_working_directory="tests/tex_project_revtex4-2",
        input_tex="main.tex",
        embed_bbl=True,
    )
