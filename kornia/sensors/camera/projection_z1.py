"""Module for the projection of points in the canonical z=1 plane."""
# inspired by: https://github.com/farm-ng/sophus-rs/blob/main/src/sensor/perspective_camera.rs
from __future__ import annotations

from typing import Optional

import kornia.core as ops
from kornia.core import Tensor
from kornia.core.check import KORNIA_CHECK_SHAPE


def project_points_z1(points_in_camera: Tensor) -> Tensor:
    """Project one or more points from the camera frame into the canonical z=1 plane through perspective division.

    Project one or more 3-points from the camera frame into the canonical
    z=1 plane through perspective division. For N points, a 3xN matrix must be
    provided where each column is a point to be transformed. The result will
    be a 2xN matrix. N may be dynamically sized, but the input columns must be
    statically determined as 3 at compile time.

    Args:
        points_in_camera: Tensor representing the points to project with shape (..., 3).

    Returns:
        Tensor representing the projected points with shape (..., 2).

    Example:
        >>> points = torch.tensor([1., 2., 3.])
        >>> project_points_z1(points)
        tensor([0.3333, 0.6667])
    """
    KORNIA_CHECK_SHAPE(points_in_camera, ["*", "3"])
    return points_in_camera[..., :2] / (points_in_camera[..., 2:3] + 1e-08)


def unproject_points_z1(points_in_cam_canonical: Tensor, extension: Optional[Tensor] = None) -> Tensor:
    """Unproject one or more points from the canonical z=1 plane into the camera frame.

    Args:
        points_in_cam_canonical: Tensor representing the points to unproject with shape (..., 2).
        extension: Tensor representing the extension of the points to unproject with shape (..., 1).

    Returns:
        Tensor representing the unprojected points with shape (..., 3).

    Example:
        >>> points = torch.tensor([1., 2.])
        >>> extension = torch.tensor([3.])
        >>> unproject_points_z1(points, extension)
        tensor([3., 6., 3.])
    """
    KORNIA_CHECK_SHAPE(points_in_cam_canonical, ["*", "2"])

    if extension is None:
        extension = ops.ones_like(points_in_cam_canonical[..., :1])
    elif extension.shape[0] > 1:
        extension = extension[..., None]  # (..., 1)

    return ops.concatenate([points_in_cam_canonical * extension, extension], dim=-1)


def dx_project_points_z1(points_in_camera: Tensor) -> Tensor:
    """Compute the derivative of the x projection with respect to the x coordinate.

    Returns point derivative of inverse depth point projection with respect to the x coordinate.

    Args:
        points_in_camera: Tensor representing the points to project with shape (..., 3).

    Returns:
        Tensor representing the derivative of the x projection with respect to the x coordinate with shape (..., 2, 3).

    Example:
        >>> points = torch.tensor([1., 2., 3.])
        >>> dx_project_points_z1(points)
        tensor([[ 0.3333,  0.0000, -0.1111],
                [ 0.0000,  0.3333, -0.2222]])
    """
    KORNIA_CHECK_SHAPE(points_in_camera, ["*", "3"])

    x = points_in_camera[..., 0]
    y = points_in_camera[..., 1]
    z = points_in_camera[..., 2]

    z_inv = 1.0 / (z + 1e-08)
    z_sq = z_inv * z_inv
    zeros = ops.zeros_like(z_inv)
    return ops.stack(
        [
            ops.stack([z_inv, zeros, -x * z_sq], dim=-1),
            ops.stack([zeros, z_inv, -y * z_sq], dim=-1),
        ],
        dim=-2,
    )
