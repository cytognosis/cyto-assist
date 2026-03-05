> **Navigation**: [← Design Index](../README.md) · [Research](README.md) · [Architecture](../architecture/README.md) · [Products](../products/README.md)

# Large-Scale Data Storage Assessment
## For Biomedical, Genomics & ML Workflows

---

# Comparison Matrix

| Feature | **AnnData** | **TileDB-SOMA** | **Zarr** | **xarray** | **Dask** |
|---------|:---:|:---:|:---:|:---:|:---:|
| **Core Identity** | Single-cell data structure | Cloud-native array platform | Chunked array format | Labeled multi-dim arrays | Parallel computing |
| **Language Support** | | | | | |
| Python | ✅ Native | ✅ Native | ✅ Native | ✅ Native | ✅ Native |
| R | ✅ (via anndata2ri) | ✅ (R-tiledbsoma) | ⚠️ (pizzarr) | ❌ | ❌ |
| Julia | ⚠️ (Muon.jl) | ⚠️ | ⚠️ | ❌ | ❌ |
| C/C++ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Data Type Support** | | | | | |
| Dense matrices | ✅ | ✅ | ✅ | ✅ | ✅ |
| Sparse matrices | ✅ (CSR/CSC) | ✅ (sparse arrays) | ⚠️ | ⚠️ | ⚠️ |
| Tensors (>2D) | ⚠️ (obsm/layers) | ✅ | ✅ | ✅ | ✅ |
| Strings/categoricals | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Storage** | | | | | |
| Storage-backed lazy loading | ⚠️ (backed mode) | ✅ Cloud-native | ✅ Chunked | ✅ (via Zarr/Dask) | ✅ |
| Cloud object store (S3) | ⚠️ | ✅ Optimized | ✅ | ✅ (via Zarr) | ✅ |
| Local filesystem | ✅ (H5AD) | ✅ | ✅ | ✅ | ✅ |
| File format | H5AD (HDF5) | TileDB arrays | Zarr stores | NetCDF/Zarr/HDF5 | N/A (lazy) |
| **Metadata & Querying** | | | | | |
| Separate data + metadata | ✅ (obs/var) | ✅ (obs/var/metadata) | ⚠️ (attrs) | ✅ (coords/dims/attrs) | ⚠️ |
| Query by metadata | ⚠️ (pandas filtering) | ✅ (TileDB query engine) | ⚠️ | ✅ (xarray.sel) | ⚠️ |
| SQL-like queries | ❌ | ✅ (TileDB Cloud) | ❌ | ❌ | ❌ |
| Version control | ❌ | ✅ (time-travel) | ❌ | ❌ | ❌ |
| **Access Patterns** | | | | | |
| Sequential | ✅ | ✅ | ✅ | ✅ | ✅ |
| Random access | ⚠️ (full load) | ✅ (efficient) | ✅ (by chunk) | ✅ (via Zarr) | ✅ |
| Distributed | ❌ | ✅ (TileDB Cloud) | ✅ (via Dask) | ✅ (via Dask) | ✅ Native |
| Chunked streaming | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| **Community Adoption** | | | | | |
| Medical/Genomics | 🟢 Standard (scRNA-seq) | 🟢 Growing (CZI partnership) | 🟡 Growing | 🟡 Limited | 🟡 General |
| AI/ML | 🟡 Limited | 🟢 Growing | 🟢 Good | 🟢 Good | 🟢 Good |
| Climate/Earth science | ❌ | ⚠️ | 🟢 Standard | 🟢 Standard | 🟢 Standard |
| **PyTorch Integration** | | | | | |
| Native DataLoader | ⚠️ (AnnLoader) | ✅ (CellArr loader) | ⚠️ (custom) | ⚠️ (custom, deadlocks) | ⚠️ (careful config) |
| IterableDataset | ✅ (scDataset) | ✅ | ✅ (custom) | ⚠️ | ⚠️ |
| Multi-worker loading | 🟡 Limited | ✅ | 🟡 (deadlock risk) | 🟡 (deadlock risk) | 🟡 |
| GPU data transfer | ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ |

---

# Recommendations

## Primary Stack for Biomedical ML

| Layer | Tool | Justification |
|-------|------|------|
| **Single-cell data** | AnnData (small/medium) → TileDB-SOMA (large) | AnnData is community standard; TileDB-SOMA scales to 100M+ cells |
| **Array storage (cloud)** | TileDB | Best cloud performance (2.3-9.3x vs Zarr), versioning, query engine |
| **Array storage (local/interop)** | Zarr v3 | Open format, excellent Dask integration, growing ecosystem |
| **Labeled dimensions** | xarray | DataTree for hierarchical data, coordinate-aware operations |
| **Parallel computing** | Dask | Essential for scaling xarray/Zarr beyond memory |
| **PyTorch loading** | `CellArr` (TileDB) / `scDataset` (AnnData) | Dedicated single-cell ML dataloaders |

## Architecture

```
Raw Data → AnnData (analysis) → TileDB-SOMA (storage)
                                      ↕
                              PyTorch DataLoader
                                      ↕
                                 GPU Training
```

For non-single-cell data:
```
Raw Data → xarray (labeled access) → Zarr (chunked storage) → Dask (parallel) → PyTorch
```

## Key Decisions

1. **TileDB-SOMA for single-cell at scale**: CZI partnership, native AnnData ingestion, best cloud I/O
2. **Zarr for general arrays**: Open format, excellent interop, Dask-native
3. **xarray for labeled access**: Coordinate-aware, HDF5/Zarr/NetCDF backends
4. **Dask for parallelism**: Required for >memory datasets, integrates with all above
5. **AnnData stays central**: Community standard API, even when backed by TileDB-SOMA
