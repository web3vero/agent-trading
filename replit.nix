{ pkgs }: {
    deps = [
        pkgs.python310Full
        pkgs.python310Packages.fastapi
        pkgs.python310Packages.uvicorn
        pkgs.python310Packages.pip
        pkgs.python310Packages.python-multipart
        pkgs.python310Packages.jinja2
        pkgs.python310Packages.python-dotenv
        pkgs.nodejs
        pkgs.nodePackages.typescript-language-server
        pkgs.yarn
        pkgs.replitPackages.jest
    ];
} 