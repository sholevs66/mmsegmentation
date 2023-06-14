# model settings
_base_ = [
    '../_base_/datasets/cityscapes.py', '../_base_/default_runtime.py',
]

# optimizer
optimizer = dict(type='Adam', lr=0.001, weight_decay=1e-5)
optim_wrapper = dict(type='OptimWrapper', optimizer=optimizer, clip_grad=None)

# learning policy
param_scheduler = [
	dict(
		type='LinearLR', start_factor=0.2, by_epoch=True, begin=0, end=5),
    dict(
        type='CosineAnnealingLR', begin=5, by_epoch=True, end=40)
]

# runtime settings
train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=40, val_interval=1)
val_cfg = dict(type='ValLoop')
test_cfg = dict(type='TestLoop')

# default hooks - logger & checkpoint configs
default_hooks = dict(

    # print log every 100 iterations.
    logger=dict(type='LoggerHook', interval=100, log_metric_by_epoch=False),

    # enable the parameter scheduler.
    param_scheduler=dict(type='ParamSchedulerHook'),

    # save checkpoint every 5 epochs.
    checkpoint=dict(type='CheckpointHook', by_epoch=True, interval=5),
)

log_processor = dict(
    by_epoch=True
)

# override train_dataloader sampler to work with epochs
train_dataloader = dict(sampler=None)

# tensorboard vis
vis_backends = [dict(type='LocalVisBackend'),
                dict(type='TensorboardVisBackend')]

# data preprocessing
norm_cfg = dict(type='SyncBN', requires_grad=True)
crop_size = (512, 1024)
data_preprocessor = dict(
    type='SegDataPreProcessor',
    mean=[123.675, 116.28, 103.53],
    std=[58.395, 57.12, 57.375],
    bgr_to_rgb=True,
    pad_val=0,
    seg_pad_val=255,
    size=crop_size)

model = dict(
    type='EncoderDecoder',
    pretrained='torchvision://resnet18',
    backbone=dict(
        type='ResNet',
        depth=18,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        dilations=(1, 1, 1, 1),
        strides=(1, 2, 2, 2),
        norm_cfg=norm_cfg,
        norm_eval=False,
        style='pytorch',
        contract_dilation=True),
    decode_head=dict(
        type='FCNGenHead',
        in_channels=[256, 512],
        input_transform='multiple_select',
        in_index=[2, 3],
        channels=512,
        num_convs=0,
        concat_input=False,
        dropout_ratio=0.1,
        num_classes=19,
        norm_cfg=norm_cfg,
        align_corners=True,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    # model training and testing settings
    train_cfg=dict(),
    test_cfg=dict(mode='whole'),
    infer_wo_softmax=True)