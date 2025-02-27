from typing import Dict
import numpy as np
import tarfile
import os
from urllib.request import urlretrieve
from gym import Env
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm


def run_episode(
    env: Env,
    agent,
    max_steps: int,
    start_pos=None,
    objects: Dict = None,
    random_start: bool = False,
    update_agent: bool = True,
    time_penalty: float = 0.0,
    collect_states: bool = False,
):
    """
    Performs a single episode of actions with the policy
    of a given agent in a given environment.
    """
    obs = env.reset(
        agent_pos=start_pos,
        objects=objects,
        random_start=random_start,
        time_penalty=time_penalty,
    )
    agent.reset()
    steps = 0
    episode_return = 0
    done = False
    if collect_states:
        states = []
    while not done and steps < max_steps:
        act = agent.sample_action(obs)
        obs_new, reward, done, _ = env.step(act)
        if update_agent:
            _ = agent.update([obs, act, obs_new, reward, done])
        if collect_states:
            states.append(obs)
        obs = obs_new
        steps += 1
        episode_return += reward
    if collect_states:
        return agent, steps, episode_return, states
    else:
        return agent, steps, episode_return


def onehot(value: int, max_value: int):
    """
    Creates a onehot encoding of an integer number.
    """
    vec = np.zeros(max_value, dtype=np.int32)
    value = np.clip(value, 0, max_value - 1)
    vec[value] = 1
    return vec


def twohot(value, max_value):
    """
    Creates a two-hot encoding of a given pair of integers.
    """
    vec_1 = np.zeros(max_value, dtype=np.float32)
    vec_2 = np.zeros(max_value, dtype=np.float32)
    vec_1[value[0]] = 1
    vec_2[value[1]] = 1
    return np.concatenate([vec_1, vec_2])


def create_circular_mask(h, w, center=None, radius=None):
    if center is None:
        center = [int(w / 2), int(h / 2)]
    if radius is None:
        radius = min(center[0], center[1], w - center[0], h - center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    mask = dist_from_center <= radius
    return mask


def softmax(x, axis=-1):
    """
    Computes the softmax function on a given vector.
    """
    e_x = np.exp(x - np.max(x))
    return e_x / np.sum(e_x, axis=axis)


def plot_values_and_policy(
    agent,
    env,
    start_pos: list,
    plot_title: str = None,
    rollout: bool = True,
    objects: dict = None,
    subplot=None,
    plot_sr=None,
):
    """
    Plots the V(s) and argmax policy for a given agent in a given environment.
    Agent must have an `agent.Q` function.
    """
    arrows = [
        [0, 0.5, 0, -0.5],
        [-0.5, 0, 0.5, 0],
        [0, -0.5, 0, 0.5],
        [0.5, 0, -0.5, 0],
        [0, 0, 0, 0],
    ]

    states = []
    if rollout:
        _, _, _, states = run_episode(
            env,
            agent,
            100,
            start_pos,
            collect_states=True,
            update_agent=False,
            objects=objects,
        )

    if objects is None:
        objects = env.topo_objects

    if subplot is None:
        _, ax = plt.subplots()
    else:
        ax = subplot
    cmap = cm.get_cmap("RdBu")
    blue = cmap(1.0)
    red = cmap(0.0)

    if agent is not None:
        V = agent.Q.mean(0)
    else:
        V = np.zeros([env.grid_size, env.grid_size])
    if plot_sr is None:
        im = ax.imshow(
            V.reshape(env.grid_size, env.grid_size), cmap="RdBu", vmin=-1.0, vmax=1.0
        )
    else:
        im = ax.imshow(plot_sr, cmap="PiYG", vmin=-1.0, vmax=1.0)
    for i in range(env.grid_size):
        for j in range(env.grid_size):
            if rollout:
                if env.get_observation([i, j]) in states:
                    use_alpha = 1.0
                else:
                    use_alpha = 0.25
            else:
                use_alpha = 0.5
            if agent is not None:
                use_dir = agent.Q.argmax(0).reshape(env.grid_size, env.grid_size)[i, j]
                use_arrow = arrows[use_dir].copy()
                use_arrow[0] += j
                use_arrow[1] += i
            if [i, j] not in env.blocks:
                if [i, j] == list(start_pos):
                    ax.text(
                        j,
                        i + 0.25,
                        "S",
                        fontdict={"fontsize": 16, "weight": "bold", "ha": "center"},
                    )
                elif (i, j) in objects['rewards'].keys():
                    reward_val = objects['rewards'][(i, j)]
                    if reward_val > 0:
                        use_color = cmap(0.75)
                    else:
                        use_color = cmap(0.25)
                    box = patches.Rectangle(
                        (j - 0.5, i - 0.5), 1.0, 1.0, color=use_color, alpha=0.5
                    )
                    ax.add_patch(box)
                    ax.text(
                        j,
                        i + 0.15,
                        str(reward_val),
                        fontdict={"fontsize": 11, "ha": "center"},
                    )
                else:
                    if agent is not None and plot_sr is None:
                        ax.arrow(
                            use_arrow[0],
                            use_arrow[1],
                            use_arrow[2],
                            use_arrow[3],
                            head_width=0.33,
                            head_length=0.33,
                            fc="k",
                            ec="k",
                            alpha=use_alpha,
                        )
            else:
                box = patches.Rectangle(
                    (j - 0.33, i - 0.33), 0.66, 0.66, color="black", alpha=0.25
                )
                ax.add_patch(box)
    if agent is not None:
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Value Estimates", rotation=270, labelpad=20, fontsize=14)
    if plot_title != None:
        ax.set_title(plot_title)
    plt.tick_params(axis="both", labelsize=0, length=0)
    return ax


# Taken from https://mattpetersen.github.io/load-cifar10-with-numpy
def cifar10(path=None):
    r"""Return (train_images, train_labels, test_images, test_labels).

    Args:
        path (str): Directory containing CIFAR-10. Default is
            /home/USER/data/cifar10 or C:\Users\USER\data\cifar10.
            Create if nonexistant. Download CIFAR-10 if missing.

    Returns:
        Tuple of (train_images, train_labels, test_images, test_labels), each
            a matrix. Rows are examples. Columns of images are pixel values,
            with the order (red -> blue -> green). Columns of labels are a
            onehot encoding of the correct class.
    """
    url = "https://www.cs.toronto.edu/~kriz/"
    tar = "cifar-10-binary.tar.gz"
    files = [
        "cifar-10-batches-bin/data_batch_1.bin",
        "cifar-10-batches-bin/data_batch_2.bin",
        "cifar-10-batches-bin/data_batch_3.bin",
        "cifar-10-batches-bin/data_batch_4.bin",
        "cifar-10-batches-bin/data_batch_5.bin",
        "cifar-10-batches-bin/test_batch.bin",
    ]

    if path is None:
        # Set path to /home/USER/data/mnist or C:\Users\USER\data\mnist
        path = os.path.join(os.path.expanduser("~"), "data", "cifar10")

    # Create path if it doesn't exist
    os.makedirs(path, exist_ok=True)

    # Download tarfile if missing
    if tar not in os.listdir(path):
        urlretrieve("".join((url, tar)), os.path.join(path, tar))
        print("Downloaded %s to %s" % (tar, path))

    # Load data from tarfile
    with tarfile.open(os.path.join(path, tar)) as tar_object:
        # Each file contains 10,000 color images and 10,000 labels
        fsize = 10000 * (32 * 32 * 3) + 10000

        # There are 6 files (5 train and 1 test)
        buffr = np.zeros(fsize * 6, dtype="uint8")

        # Get members of tar corresponding to data files
        # -- The tar contains README's and other extraneous stuff
        members = [file for file in tar_object if file.name in files]

        # Sort those members by name
        # -- Ensures we load train data in the proper order
        # -- Ensures that test data is the last file in the list
        members.sort(key=lambda member: member.name)

        # Extract data from members
        for i, member in enumerate(members):
            # Get member as a file object
            f = tar_object.extractfile(member)
            # Read bytes from that file object into buffr
            buffr[i * fsize : (i + 1) * fsize] = np.frombuffer(f.read(), "B")

    # Parse data from buffer
    # -- Examples are in chunks of 3,073 bytes
    # -- First byte of each chunk is the label
    # -- Next 32 * 32 * 3 = 3,072 bytes are its corresponding image

    # Labels are the first byte of every chunk
    labels = buffr[::3073]

    # Pixels are everything remaining after we delete the labels
    pixels = np.delete(buffr, np.arange(0, buffr.size, 3073))
    images = (pixels.reshape(-1, 3072).astype("float32") / 255).reshape(
        -1, 32, 32, 3, order="F"
    )

    # Split into train and test
    train_images, test_images = images[:50000], images[50000:]
    train_labels, test_labels = labels[:50000], labels[50000:]

    def _onehot(integer_labels):
        """Return matrix whose rows are onehot encodings of integers."""
        n_rows = len(integer_labels)
        n_cols = integer_labels.max() + 1
        onehot = np.zeros((n_rows, n_cols), dtype="uint8")
        onehot[np.arange(n_rows), integer_labels] = 1
        return onehot

    return train_images, _onehot(train_labels), test_images, _onehot(test_labels)
