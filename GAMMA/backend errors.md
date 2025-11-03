2025-11-03T10:35:36.000000000Z [inf]  Starting Container
2025-11-03T10:35:38.658559639Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:38.658569676Z [err]      server.run()
2025-11-03T10:35:38.658575628Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:38.658586198Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:38.658592403Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.658597746Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:38.658603278Z [err]      return runner.run(main)
2025-11-03T10:35:38.658657881Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.658662342Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:38.658666913Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:38.658671454Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.658675987Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:38.658680465Z [err]      run(
2025-11-03T10:35:38.658876911Z [err]  Traceback (most recent call last):
2025-11-03T10:35:38.658883993Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:38.658890023Z [err]      sys.exit(main())
2025-11-03T10:35:38.658897265Z [err]               ^^^^^^
2025-11-03T10:35:38.658904139Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:38.658912020Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:38.658918027Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.658923269Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:38.658929013Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:38.658935091Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.658943547Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:38.658949771Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:38.660412240Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.660417374Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:38.660421384Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:38.660427186Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.660433845Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:38.660437936Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:38.660442145Z [err]      config.load()
2025-11-03T10:35:38.660446333Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:38.660450584Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:38.660454686Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.660458453Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:38.660463210Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:38.662055883Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.662061770Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:38.662067268Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:38.662071337Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.662075565Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:38.662081124Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:38.662085895Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:38.662091258Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:38.662096419Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:38.662100702Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:38.662104864Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:38.662110199Z [err]      from config import settings
2025-11-03T10:35:38.662117446Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:38.663552768Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:38.663559623Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:38.663564869Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:38.663571404Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:38.663576831Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:38.663581094Z [err]      raise PydanticImportError(
2025-11-03T10:35:38.663585452Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:38.663589799Z [err]  
2025-11-03T10:35:38.663594300Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:39.648219584Z [err]      return runner.run(main)
2025-11-03T10:35:39.648222377Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:39.648232060Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.648241066Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:39.648248295Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:39.648254929Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.648262952Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:39.648269458Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:39.648562934Z [err]  Traceback (most recent call last):
2025-11-03T10:35:39.648572103Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:39.648577907Z [err]      sys.exit(main())
2025-11-03T10:35:39.648583594Z [err]               ^^^^^^
2025-11-03T10:35:39.648589402Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:39.648595115Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:39.648601011Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.648607495Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:39.648614460Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:39.648620626Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.648628024Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:39.648634222Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:39.648639996Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.648645900Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:39.648659163Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:39.648800015Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.648809672Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:39.648815871Z [err]      run(
2025-11-03T10:35:39.648821913Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:39.648828362Z [err]      server.run()
2025-11-03T10:35:39.648834100Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:39.648842294Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:39.648848776Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.649852800Z [err]      config.load()
2025-11-03T10:35:39.649857736Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:39.649863724Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:39.649870682Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.649877018Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:39.649883531Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:39.649889408Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.649895585Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:39.649901984Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:39.649908134Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.651015288Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:39.651020497Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:39.651025952Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:39.651031270Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:39.651036578Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:39.651041840Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:39.651046760Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:39.651051877Z [err]      from config import settings
2025-11-03T10:35:39.651057461Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:39.651063584Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:39.651068956Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:39.651096180Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:39.651101558Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:39.651106831Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:39.651112103Z [err]      raise PydanticImportError(
2025-11-03T10:35:39.651117947Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:39.651762366Z [err]  
2025-11-03T10:35:39.651768069Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:41.126984940Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:41.126998159Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:41.127006847Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.127016518Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:41.127028293Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:41.127041199Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.127050489Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:41.127063133Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:41.127067164Z [err]  Traceback (most recent call last):
2025-11-03T10:35:41.127088994Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:41.127096932Z [err]      sys.exit(main())
2025-11-03T10:35:41.127104180Z [err]               ^^^^^^
2025-11-03T10:35:41.127111090Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:41.127118054Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:41.127125952Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.129209558Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.129225048Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:41.129233799Z [err]      run(
2025-11-03T10:35:41.129246599Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:41.129254762Z [err]      server.run()
2025-11-03T10:35:41.129263516Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:41.129271195Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:41.129279095Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.129287641Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:41.129297439Z [err]      return runner.run(main)
2025-11-03T10:35:41.129306540Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.129314309Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:41.129324585Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:41.130828164Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.130835079Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:41.130841403Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:41.130849223Z [err]      config.load()
2025-11-03T10:35:41.130854642Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:41.130859429Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:41.130864932Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.130870043Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:41.130874956Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:41.130880275Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.130885278Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:41.130889879Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:41.132730431Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.132730858Z [err]      from config import settings
2025-11-03T10:35:41.132740513Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:41.132741673Z [err]  ^^^^^
2025-11-03T10:35:41.132748502Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:41.132750618Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:41.132754225Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:41.132758965Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:41.132761167Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:41.132766972Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:41.132773010Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:41.132779093Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:41.132785246Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:41.132791988Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:41.135043649Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:41.135049798Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:41.135054938Z [err]      raise PydanticImportError(
2025-11-03T10:35:41.135060262Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:41.135086851Z [err]  
2025-11-03T10:35:41.135096288Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:43.016939748Z [err]  Traceback (most recent call last):
2025-11-03T10:35:43.016956450Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:43.016965630Z [err]      sys.exit(main())
2025-11-03T10:35:43.016973515Z [err]               ^^^^^^
2025-11-03T10:35:43.016981544Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:43.016991126Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:43.017001453Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.017009207Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:43.017017301Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:43.017026336Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.017034072Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:43.017041199Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:43.017049573Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.017056978Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:43.020331348Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:43.020345041Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:43.020350976Z [err]      return runner.run(main)
2025-11-03T10:35:43.020360314Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.020364660Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.020371158Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:43.020374244Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:43.020380380Z [err]      run(
2025-11-03T10:35:43.020389174Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:43.020396092Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:43.020547390Z [err]      server.run()
2025-11-03T10:35:43.020557125Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:43.020563240Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:43.020569712Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.024004800Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:43.024018145Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.024019419Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:43.024029939Z [err]      config.load()
2025-11-03T10:35:43.024037985Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:43.024046682Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:43.024053943Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.024059813Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:43.024066192Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:43.024077835Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.025829578Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:43.025836564Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:43.025842346Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.025847654Z [err]  ^^^^^^^^
2025-11-03T10:35:43.025853055Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:43.025859075Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:43.025867636Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:43.025875164Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:43.025881855Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:43.025888023Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:43.025893904Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:43.025899801Z [err]      from config import settings
2025-11-03T10:35:43.025906802Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:43.025912642Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:43.025918556Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:43.025924179Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:43.027559476Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:43.027569976Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:43.027577164Z [err]      raise PydanticImportError(
2025-11-03T10:35:43.027583562Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:43.027590079Z [err]  
2025-11-03T10:35:43.027597037Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:44.897921725Z [err]  Traceback (most recent call last):
2025-11-03T10:35:44.897922179Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.897932802Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:44.897934271Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:44.897941077Z [err]      sys.exit(main())
2025-11-03T10:35:44.897944137Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:44.897949790Z [err]               ^^^^^^
2025-11-03T10:35:44.897953049Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.897959019Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:44.897962206Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:44.897968261Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:44.897969410Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:44.897976024Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.897976699Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.897982313Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:44.897984537Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:44.897992264Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:44.899344358Z [err]      run(
2025-11-03T10:35:44.899356086Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:44.899369757Z [err]      server.run()
2025-11-03T10:35:44.899379139Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:44.899387757Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:44.899397715Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.899406796Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:44.899415374Z [err]      return runner.run(main)
2025-11-03T10:35:44.899423875Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.899432402Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:44.899442763Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:44.899451773Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.899460112Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:44.899469680Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:44.901141837Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:44.901145983Z [err]      config.load()
2025-11-03T10:35:44.901151687Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:44.901156290Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:44.901161046Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.901165507Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:44.901172821Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:44.901177667Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.901182256Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:44.904583810Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:44.904594294Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:44.904601861Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:44.904609289Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:44.904618756Z [err]      from config import settings
2025-11-03T10:35:44.904626258Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:44.904632250Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:44.904638175Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:44.904644441Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:44.904750128Z [err]             ^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.904762678Z [err]  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.904766909Z [err]  ^^^^
2025-11-03T10:35:44.904774306Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:44.904780597Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:44.904797647Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:44.906480467Z [err]  
2025-11-03T10:35:44.906490126Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:44.906493788Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:44.906498137Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:44.906504072Z [err]      raise PydanticImportError(
2025-11-03T10:35:44.906509717Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:46.682595655Z [err]  Traceback (most recent call last):
2025-11-03T10:35:46.682598621Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:46.682611502Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:46.682620928Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.682622748Z [err]      sys.exit(main())
2025-11-03T10:35:46.682632472Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:46.682635599Z [err]               ^^^^^^
2025-11-03T10:35:46.682645162Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:46.682652730Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:46.682659618Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.682667501Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:46.682674610Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:46.682682088Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.682691805Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:46.684916594Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.684930338Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:46.684934697Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:46.684939770Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.684941441Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:46.684945160Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:46.684949933Z [err]      run(
2025-11-03T10:35:46.684955327Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:46.684961891Z [err]      server.run()
2025-11-03T10:35:46.684966601Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:46.684971580Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:46.684976605Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.684980859Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:46.684985199Z [err]      return runner.run(main)
2025-11-03T10:35:46.686539465Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:46.686548737Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:46.686556975Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.686560567Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.686568694Z [err]  ^
2025-11-03T10:35:46.686576119Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:46.686583785Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:46.686586779Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:46.686596555Z [err]      config.load()
2025-11-03T10:35:46.686600402Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:46.686604463Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:46.686609150Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:46.686614095Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.689284675Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.689289151Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:46.689303649Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:46.689307679Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:46.689319528Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:46.689321347Z [err]      raise PydanticImportError(
2025-11-03T10:35:46.689332498Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:46.689339355Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:46.689353901Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:46.689365329Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:46.689373818Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:46.689380278Z [err]      from config import settings
2025-11-03T10:35:46.689387097Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:46.689394403Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:46.689401618Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:46.689408405Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:46.690314680Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:46.690320229Z [err]  
2025-11-03T10:35:46.690324976Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:48.663831125Z [err]  Traceback (most recent call last):
2025-11-03T10:35:48.663839361Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:48.663846393Z [err]      sys.exit(main())
2025-11-03T10:35:48.663852652Z [err]               ^^^^^^
2025-11-03T10:35:48.663859884Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:48.663865749Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:48.663872784Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.663879024Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:48.663913247Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:48.663919218Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.663925393Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:48.663932201Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:48.663938872Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.663944691Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:48.663951241Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:48.663957536Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.663964852Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:48.664696757Z [err]      run(
2025-11-03T10:35:48.664702325Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:48.664708326Z [err]      server.run()
2025-11-03T10:35:48.664713834Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:48.664724213Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:48.664731208Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.664738242Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:48.664745289Z [err]      return runner.run(main)
2025-11-03T10:35:48.664751105Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.664756804Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:48.664762303Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:48.664767284Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.664773429Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:48.664779464Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:48.665802425Z [err]      config.load()
2025-11-03T10:35:48.665806673Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:48.665810910Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:48.665814551Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.665818989Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:48.665823088Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:48.665827507Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.665832075Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:48.665836504Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:48.665841260Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.665854890Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:48.665859749Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:48.667407292Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:48.667411238Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:48.667415262Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:48.667419408Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:48.667424092Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:48.667428462Z [err]      from config import settings
2025-11-03T10:35:48.667550531Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:48.667555560Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:48.667560636Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:48.667564761Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:48.667568756Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:48.667574255Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:48.667578830Z [err]      raise PydanticImportError(
2025-11-03T10:35:48.667582447Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:48.667587775Z [err]  
2025-11-03T10:35:48.667592077Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:50.235440071Z [err]  Traceback (most recent call last):
2025-11-03T10:35:50.235449693Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:50.235455923Z [err]      sys.exit(main())
2025-11-03T10:35:50.235461011Z [err]            
2025-11-03T10:35:50.235465619Z [err]     ^^^^^^
2025-11-03T10:35:50.235470401Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:50.235474929Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:50.235479781Z [err]            
2025-11-03T10:35:50.238281026Z [err]   ^^^^^^^^^
2025-11-03T10:35:50.238286399Z [err]  ^^^^^^^^^^
2025-11-03T10:35:50.238292913Z [err]  ^^^^^^^
2025-11-03T10:35:50.238299374Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:50.238304457Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:50.238310268Z [err]           ^
2025-11-03T10:35:50.240051393Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.240066991Z [err]  ^^^^^^^^^^
2025-11-03T10:35:50.240072164Z [err]  ^^^^^
2025-11-03T10:35:50.240076690Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:50.240081382Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:50.240086024Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.240090881Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:50.240096255Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:50.240102564Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.240109163Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:50.240116619Z [err]      run(
2025-11-03T10:35:50.240122212Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:50.240128340Z [err]      server.run()
2025-11-03T10:35:50.240133603Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:50.240139252Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:50.242104575Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:50.242115171Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:50.242116149Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:50.242121863Z [err]      return runner.run(main)
2025-11-03T10:35:50.242124820Z [err]      config.load()
2025-11-03T10:35:50.242127569Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.242133895Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:50.242135011Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:50.242140693Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:50.242144909Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:50.242146483Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.242152015Z [err]  
2025-11-03T10:35:50.242153818Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.242158720Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:50.244202676Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:50.244208683Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:50.244215415Z [err]      from config import settings
2025-11-03T10:35:50.244217218Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.244223957Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:50.244225280Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:50.244231561Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:50.244236868Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.244242364Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:50.244248484Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:50.244254980Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:50.244262967Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:50.244268691Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:50.244274903Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:50.245945346Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:50.245953257Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:50.245959574Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:50.245966165Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:50.245971939Z [err]  ^
2025-11-03T10:35:50.245979246Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:50.245985174Z [err]      raise PydanticImportError(
2025-11-03T10:35:50.245991628Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:50.245998042Z [err]  
2025-11-03T10:35:50.246003879Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:52.137266458Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.137279450Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:52.137290899Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:52.137300697Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.137304980Z [err]  Traceback (most recent call last):
2025-11-03T10:35:52.137310539Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:52.137311843Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:52.137316214Z [err]      sys.exit(main())
2025-11-03T10:35:52.137322702Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:52.137324216Z [err]               ^^^^^^
2025-11-03T10:35:52.137329997Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:52.137334826Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:52.137359164Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.137378046Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:52.137387429Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:52.137400922Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.137409802Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:52.137418439Z [err]      run(
2025-11-03T10:35:52.137432493Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:52.137442251Z [err]      server.run()
2025-11-03T10:35:52.138901999Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:52.138911205Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:52.138911915Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:52.138919081Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.138924246Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:52.138926988Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:52.138933217Z [err]      return runner.run(main)
2025-11-03T10:35:52.138939493Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.138943389Z [err]      config.load()
2025-11-03T10:35:52.138947802Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:52.138952291Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:52.138955003Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:52.138960003Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.141668471Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:52.141680477Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.141692058Z [err]  ^^^
2025-11-03T10:35:52.141699262Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:52.141709216Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:52.141719222Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.141727346Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:52.141733475Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:52.141739048Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.143619671Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:52.143632435Z [err]  ^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.143637682Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:52.143643170Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:52.143648513Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:52.143653180Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:52.143658077Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:52.143662862Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:52.143668874Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:52.143674519Z [err]      from config import settings
2025-11-03T10:35:52.143679042Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:52.143685381Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:52.143690733Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:52.143696823Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:52.143703259Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:52.143710147Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:52.143716942Z [err]      raise PydanticImportError(
2025-11-03T10:35:52.144380780Z [err]  
2025-11-03T10:35:52.144387782Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:54.051784882Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.051797787Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:54.051805020Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:54.051928649Z [err]  Traceback (most recent call last):
2025-11-03T10:35:54.051935843Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:54.051943641Z [err]      sys.exit(main())
2025-11-03T10:35:54.051950078Z [err]               ^^^^^^
2025-11-03T10:35:54.051956594Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:54.051964113Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:54.051974062Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.051981197Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:54.051988571Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:54.051994864Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.052002069Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:54.052010852Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:54.052480959Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.052488516Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:54.052494476Z [err]      run(
2025-11-03T10:35:54.052500473Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:54.052506916Z [err]      server.run()
2025-11-03T10:35:54.052512422Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:54.052518283Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:54.052523834Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.052529352Z [err]  ^^^^^^^^^^^^^^^
2025-11-03T10:35:54.052534873Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:54.052539958Z [err]      return runner.run(main)
2025-11-03T10:35:54.052545624Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.052550935Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:54.052556302Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:54.053987607Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.053996166Z [err]  ^^
2025-11-03T10:35:54.054000685Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:54.054007434Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:54.054011833Z [err]      config.load()
2025-11-03T10:35:54.054016190Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:54.054020169Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:54.054025144Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.054031559Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:54.054038321Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:54.055621384Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:54.055623486Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.055631191Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:54.055635027Z [err]  
2025-11-03T10:35:54.055637535Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:54.055642887Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:54.055645877Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:54.055649014Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:54.055655242Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:54.055655458Z [err]      from config import settings
2025-11-03T10:35:54.055664126Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:54.055665898Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.055671097Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:54.055674124Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:54.055677192Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:54.055682164Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:54.055686580Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:54.056469837Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:54.056477021Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:54.056482462Z [err]      raise PydanticImportError(
2025-11-03T10:35:54.056488100Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:54.056494092Z [err]  
2025-11-03T10:35:54.056499456Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error
2025-11-03T10:35:55.870543139Z [err]  Traceback (most recent call last):
2025-11-03T10:35:55.870550863Z [err]    File "/opt/venv/bin/uvicorn", line 8, in <module>
2025-11-03T10:35:55.870558361Z [err]      sys.exit(main())
2025-11-03T10:35:55.870566737Z [err]               ^^^^^^
2025-11-03T10:35:55.870572446Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1462, in __call__
2025-11-03T10:35:55.873048016Z [err]      return self.main(*args, **kwargs)
2025-11-03T10:35:55.873055966Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.873061805Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1383, in main
2025-11-03T10:35:55.873066778Z [err]      rv = self.invoke(ctx)
2025-11-03T10:35:55.873071513Z [err]           ^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.873076220Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 1246, in invoke
2025-11-03T10:35:55.873080653Z [err]      return ctx.invoke(self.callback, **ctx.params)
2025-11-03T10:35:55.873085618Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.873090496Z [err]    File "/opt/venv/lib/python3.12/site-packages/click/core.py", line 814, in invoke
2025-11-03T10:35:55.873096772Z [err]      return callback(*args, **kwargs)
2025-11-03T10:35:55.873101045Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.873105707Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 416, in main
2025-11-03T10:35:55.873111144Z [err]      run(
2025-11-03T10:35:55.873116378Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/main.py", line 587, in run
2025-11-03T10:35:55.874762121Z [err]      server.run()
2025-11-03T10:35:55.874771252Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 61, in run
2025-11-03T10:35:55.874779919Z [err]      return asyncio.run(self.serve(sockets=sockets))
2025-11-03T10:35:55.874787661Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.874797371Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 194, in run
2025-11-03T10:35:55.874808479Z [err]      return runner.run(main)
2025-11-03T10:35:55.874814919Z [err]             ^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.874821739Z [err]    File "/root/.nix-profile/lib/python3.12/asyncio/runners.py", line 118, in run
2025-11-03T10:35:55.874828281Z [err]      return self._loop.run_until_complete(task)
2025-11-03T10:35:55.874835044Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.874842615Z [err]    File "uvloop/loop.pyx", line 1517, in uvloop.loop.Loop.run_until_complete
2025-11-03T10:35:55.874848723Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/server.py", line 68, in serve
2025-11-03T10:35:55.874862291Z [err]      config.load()
2025-11-03T10:35:55.874868895Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/config.py", line 467, in load
2025-11-03T10:35:55.876888909Z [err]      self.loaded_app = import_from_string(self.app)
2025-11-03T10:35:55.876896630Z [err]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.876901583Z [err]    File "/opt/venv/lib/python3.12/site-packages/uvicorn/importer.py", line 21, in import_from_string
2025-11-03T10:35:55.876906439Z [err]      module = importlib.import_module(module_str)
2025-11-03T10:35:55.876911882Z [err]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.876918440Z [err]    File "/root/.nix-profile/lib/python3.12/importlib/__init__.py", line 90, in import_module
2025-11-03T10:35:55.876924055Z [err]      return _bootstrap._gcd_import(name[level:], package, level)
2025-11-03T10:35:55.876931667Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.876936205Z [err]    File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2025-11-03T10:35:55.876941028Z [err]    File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2025-11-03T10:35:55.878346270Z [err]    File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2025-11-03T10:35:55.878352017Z [err]    File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2025-11-03T10:35:55.878358085Z [err]    File "<frozen importlib._bootstrap_external>", line 995, in exec_module
2025-11-03T10:35:55.878362989Z [err]    File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2025-11-03T10:35:55.878367627Z [err]    File "/app/main.py", line 15, in <module>
2025-11-03T10:35:55.878372794Z [err]      from config import settings
2025-11-03T10:35:55.878377065Z [err]    File "/app/config.py", line 9, in <module>
2025-11-03T10:35:55.878381086Z [err]      from pydantic import BaseSettings, validator
2025-11-03T10:35:55.878386548Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/__init__.py", line 363, in __getattr__
2025-11-03T10:35:55.878391215Z [err]      return _getattr_migration(attr_name)
2025-11-03T10:35:55.878395321Z [err]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-11-03T10:35:55.878400808Z [err]    File "/opt/venv/lib/python3.12/site-packages/pydantic/_migration.py", line 296, in wrapper
2025-11-03T10:35:55.878406179Z [err]      raise PydanticImportError(
2025-11-03T10:35:55.878411606Z [err]  pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package. See https://docs.pydantic.dev/2.5/migration/#basesettings-has-moved-to-pydantic-settings for more details.
2025-11-03T10:35:55.878416556Z [err]  
2025-11-03T10:35:55.878421702Z [err]  For further information visit https://errors.pydantic.dev/2.5/u/import-error