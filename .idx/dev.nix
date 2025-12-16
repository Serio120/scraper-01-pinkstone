# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # Create a Python environment with specific packages.
    # Nix will manage these dependencies declaratively.
    (pkgs.python3.withPackages (ps: [
      ps.requests
      ps.beautifulsoup4
      ps.pandas
      ps.openpyxl
    ]))
  ];

  # Sets environment variables in the workspace
  env = {};

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
    ];

    # Workspace lifecycle hooks
    workspace = {
      # The onCreate hook is no longer needed, as Nix now handles the packages.
      onCreate = {};

      # Runs when the workspace is (re)started
      onStart = {
        start-app = "python main.py";
      };
    };
  };
}
