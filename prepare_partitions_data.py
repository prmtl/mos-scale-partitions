import argparse
from copy import deepcopy
import json
import random

from fuel_agent.objects import FileSystem
from fuel_agent.objects import LogicalVolume
from fuel_agent.objects import Parted
from fuel_agent.objects import Partition
from fuel_agent.objects import PhysicalVolume
from fuel_agent.objects import VolumeGroup


def make_fs(disk):
    return {
        'boot': FileSystem(
            device='/dev/{}3'.format(disk['device']),
            fs_label='boot',
            fs_type='ext2',
            mount='/boot'
        ),
        'root': FileSystem(
            device='/dev/mapper/os-root',
            fs_label='root',
            fs_type='ext4',
            mount='/'
        ),
        'swap': FileSystem(
            device='/dev/mapper/os-swap',
            fs_label='',
            fs_type='swap',
            mount='swap'
        ),

    }


def make_lv(vg):
    return {
        'root': LogicalVolume(
            name='root',
            size=10000,
            vgname=vg.name,
        ),
        'swap': LogicalVolume(
            name='swap',
            size=2000,
            vgname=vg.name,
        )
    }


def make_vg(pvs):
    return {
        'os': VolumeGroup(
            name='os',
            pvnames=[pv.name for pv in pvs],
        )
    }


def make_parted_and_partitions(disk):
    device = disk['device']
    partitions = {
        device: {
            '{0}1'.format(device): Partition(
                name='/dev/{0}1'.format(device),
                device='/dev/{0}'.format(device),
                count=1,
                begin=1,
                end=25,
                guid=None,
                configdrive=False,
                flags=['bios_grub'],
                partition_type='primary',
            ),
            '{0}2'.format(device): Partition(
                name='/dev/{0}2'.format(device),
                device='/dev/{0}'.format(device),
                count=2,
                begin=25,
                end=225,
                guid=None,
                configdrive=False,
                partition_type='primary',
            ),
            '{0}3'.format(device): Partition(
                name='/dev/{0}3'.format(device),
                device='/dev/{0}'.format(device),
                count=3,
                begin=225,
                end=425,
                guid=None,
                configdrive=False,
                partition_type='primary',
            ),
            '{0}4'.format(device): Partition(
                name='/dev/{0}4'.format(device),
                device='/dev/{0}'.format(device),
                count=4,
                begin=425,
                end=20045,
                guid=None,
                configdrive=False,
                partition_type='primary',
            ),
            '{0}5'.format(device): Partition(
                name='/dev/{0}5'.format(device),
                device='/dev/{0}'.format(device),
                count=5,
                begin=20045,
                end=20445,
                guid=None,
                configdrive=True,
                partition_type='primary',
            )
        }
    }
    parted = {
        disk['device']: Parted(
            label='gpt',
            name='/dev/{0}'.format(disk['device']),
            # Partitions should be created in specific order
            partitions=sorted(partitions[device].values(),
                              key=lambda v: v.count),
            install_bootloader=True
        )

    }
    return parted, partitions


def make_pv(disk):
    return {
        '{}4'.format(disk['device']): PhysicalVolume(
            name='/dev/{0}4'.format(disk['device']),
            metadatacopies=2,
            metadatasize=28,
        )
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disk', type=str, default='sda',
                        help='Name of the disk (default sda)')
    args = parser.parse_args()

    disk = {
        'device': args.disk,
    }

    parteds, partitions = make_parted_and_partitions(disk)
    fss = make_fs(disk)
    pvs = make_pv(disk)
    vgs = make_vg(pvs.values())
    vg = vgs.values()[0]
    lvs = make_lv(vg)

    def _serialize(objs):
        return [obj.to_dict() for obj in objs.values()]

    partitioning = {
        'parteds': _serialize(parteds),
        'fss': _serialize(fss),
        'pvs': _serialize(pvs),
        'vgs': _serialize(vgs),
        'lvs': _serialize(lvs),
    }

    print(json.dumps({
        'partitioning': partitioning,
    }, indent=2))

if __name__ == '__main__':
    main()
