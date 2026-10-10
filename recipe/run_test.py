"""Exercise installed Hydra composition and instantiation with its OmegaConf dependency."""
from pathlib import Path
from tempfile import TemporaryDirectory

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from omegaconf import OmegaConf

with TemporaryDirectory() as directory:
    config_dir = Path(directory)
    (config_dir / "db").mkdir()
    (config_dir / "db" / "sqlite.yaml").write_text("port: 1234\n", encoding="utf-8")
    (config_dir / "config.yaml").write_text(
        "defaults:\n  - db: sqlite\n  - _self_\nanswer: 42\nport: ${db.port}\n",
        encoding="utf-8",
    )
    with initialize_config_dir(config_dir=str(config_dir), version_base=None):
        config = compose(config_name="config", overrides=["answer=7", "db.port=5678"])
        assert OmegaConf.to_container(config, resolve=True) == {
            "db": {"port": 5678}, "answer": 7, "port": 5678
        }

    # Initialization restores global state, so a second context must also work.
    with initialize_config_dir(config_dir=str(config_dir), version_base=None):
        assert compose(config_name="config").answer == 42

assert instantiate({"_target_": "builtins.dict", "answer": 7}) == {"answer": 7}
print("Hydra composition, overrides, interpolation, initialization, and instantiation passed.")
