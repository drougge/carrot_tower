#!/bin/sh

rm -f carrot_tower.tar.gz
cd ..
tar zcf carrot_tower/carrot_tower.tar.gz carrot_tower/LICENSE* carrot_tower/README* carrot_tower/run* carrot_tower/game/*.py carrot_tower/game/*.png carrot_tower/game/*.wav carrot_tower/game/*.jpeg
